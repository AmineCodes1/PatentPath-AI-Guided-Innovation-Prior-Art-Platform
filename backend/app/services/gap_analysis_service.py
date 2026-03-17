"""Claude Sonnet integration for generating structured patent gap analysis."""

from __future__ import annotations

import json
import re
from uuid import UUID

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models.gap_analysis import GapAnalysis, OverallRisk
from app.models.patent_record import PatentRecord
from app.models.scored_result import ScoredResult
from app.models.search_session import SearchSession
from app.schemas.gap_analysis import GapAnalysisCreate

settings = get_settings()
MODEL_NAME = "claude-sonnet-4-20250514"


def build_gap_analysis_prompt(query_text: str, top_patents: list[PatentRecord]) -> tuple[str, str]:
    """Build the system and user prompts used for Claude gap analysis generation."""
    system_prompt = (
        "You are a patent analysis assistant with expertise in prior art assessment and innovation strategy. "
        "Analyze the provided invention idea against retrieved prior art patents. "
        "Return ONLY a valid JSON object with no markdown formatting, no code blocks, no preamble."
    )

    patents_payload = [
        {
            "pub_number": patent.publication_number,
            "title": patent.title,
            "abstract": patent.abstract,
            "claims_excerpt": (patent.claims or "")[:500],
        }
        for patent in top_patents[:20]
    ]

    required_schema = {
        "overall_risk": "HIGH|MEDIUM|LOW",
        "covered_aspects": ["aspect 1", "aspect 2"],
        "gap_aspects": ["gap 1", "gap 2"],
        "suggestions": ["suggestion 1", "suggestion 2"],
        "feasibility": {
            "technical_readiness": 1,
            "domain_specificity": 1,
            "claim_potential": 1,
            "commentary": "brief explanation",
        },
        "narrative": (
            "Full markdown narrative text covering: what prior art was found, what is novel, "
            "what risks exist, recommended differentiation strategy."
        ),
    }

    user_prompt = (
        f"Invention description:\n{query_text.strip()}\n\n"
        "Prior art patents (top N, max 20):\n"
        f"{json.dumps(patents_payload, ensure_ascii=False, indent=2)}\n\n"
        "Required JSON output schema:\n"
        f"{json.dumps(required_schema, ensure_ascii=False, indent=2)}\n\n"
        "Instruction:\n"
        "covered_aspects: aspects of the invention that are anticipated by existing patents.\n"
        "gap_aspects: aspects NOT covered by prior art - these are innovation opportunities.\n"
        "suggestions: concrete technical directions to create a genuinely novel invention.\n"
        "narrative: 300-500 word professional analysis."
    )

    return system_prompt, user_prompt


def _extract_text_content(message: object) -> str:
    content = getattr(message, "content", None)
    if isinstance(content, list):
        text_parts: list[str] = []
        for block in content:
            block_text = getattr(block, "text", None)
            if block_text:
                text_parts.append(str(block_text))
        if text_parts:
            return "\n".join(text_parts).strip()

    return str(getattr(message, "text", "") or "").strip()


def _extract_json_payload(raw_text: str) -> dict[str, object]:
    cleaned = raw_text.strip()
    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, flags=re.DOTALL)
    if fenced_match:
        cleaned = fenced_match.group(1).strip()

    return json.loads(cleaned)


async def run_gap_analysis(db: AsyncSession, session_id: str) -> GapAnalysis:
    """Generate and persist Claude-based gap analysis for a completed search session."""
    session_uuid = UUID(session_id)

    cached = await db.scalar(select(GapAnalysis).where(GapAnalysis.session_id == session_uuid))
    if cached is not None:
        return cached

    session = await db.scalar(select(SearchSession).where(SearchSession.id == session_uuid))
    if session is None:
        raise ValueError(f"Search session not found: {session_id}")

    scored_rows = list(
        (
            await db.execute(
                select(ScoredResult)
                .where(
                    ScoredResult.session_id == session_uuid,
                    ScoredResult.composite_score > 0.3,
                )
                .options(selectinload(ScoredResult.patent))
                .order_by(ScoredResult.composite_score.desc())
                .limit(20)
            )
        ).scalars()
    )

    patents = [row.patent for row in scored_rows if row.patent is not None]
    system_prompt, user_prompt = build_gap_analysis_prompt(session.query_text, patents)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    message = await client.messages.create(
        model=MODEL_NAME,
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_text = _extract_text_content(message)

    try:
        parsed_json = _extract_json_payload(raw_text)
        validated = GapAnalysisCreate.model_validate(parsed_json)

        gap_analysis = GapAnalysis(
            session_id=session_uuid,
            overall_risk=validated.overall_risk,
            covered_aspects=validated.covered_aspects,
            gap_aspects=validated.gap_aspects,
            suggestions=validated.suggestions,
            narrative_text=validated.narrative_text,
            model_used=validated.model_used or MODEL_NAME,
            feasibility_technical=validated.feasibility_technical,
            feasibility_domain=validated.feasibility_domain,
            feasibility_claim=validated.feasibility_claim,
        )
    except Exception:
        # Current ORM constraints require non-null risk and list fields, so parse failures are
        # persisted with safe defaults plus a parse marker while preserving raw model output.
        gap_analysis = GapAnalysis(
            session_id=session_uuid,
            overall_risk=OverallRisk.LOW,
            covered_aspects=[],
            gap_aspects=[],
            suggestions=[],
            narrative_text=raw_text,
            model_used=f"{MODEL_NAME};parse_error=true",
            feasibility_technical=None,
            feasibility_domain=None,
            feasibility_claim=None,
        )

    db.add(gap_analysis)
    await db.commit()
    await db.refresh(gap_analysis)
    return gap_analysis
