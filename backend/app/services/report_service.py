"""Report generation service for assembling context, rendering HTML, and producing PDF bytes."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from weasyprint import HTML

from app.models.gap_analysis import GapAnalysis
from app.models.innovation_project import InnovationProject
from app.models.project_note import ProjectNote
from app.models.scored_result import ScoredResult
from app.models.search_session import SearchSession

_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
_TEMPLATE_NAME = "patent_report.html"

_jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def _compute_feasibility_composite(gap_analysis: GapAnalysis) -> float:
    scores = [
        gap_analysis.feasibility_technical,
        gap_analysis.feasibility_domain,
        gap_analysis.feasibility_claim,
    ]
    numeric_scores = [float(score) for score in scores if score is not None]
    if not numeric_scores:
        return 0.0
    return round(mean(numeric_scores) * 20, 2)


async def build_report_context(
    db: AsyncSession,
    project_id: UUID,
    session_id: UUID,
    user_id: UUID,
) -> dict[str, Any]:
    """Aggregate all entities required by the patent preparation report template."""
    project = await db.scalar(
        select(InnovationProject).where(
            InnovationProject.id == project_id,
            InnovationProject.user_id == user_id,
        )
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    session = await db.scalar(
        select(SearchSession).where(
            SearchSession.id == session_id,
            SearchSession.project_id == project_id,
        )
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search session not found")

    gap_analysis = await db.scalar(select(GapAnalysis).where(GapAnalysis.session_id == session_id))
    if gap_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gap analysis not generated for this session",
        )

    scored_rows = list(
        (
            await db.scalars(
                select(ScoredResult)
                .where(ScoredResult.session_id == session_id)
                .options(joinedload(ScoredResult.patent))
                .order_by(ScoredResult.rank.asc())
            )
        ).all()
    )

    if not scored_rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No scored results found for this session",
        )

    top_5_results: list[tuple[ScoredResult, Any]] = [
        (item, item.patent)
        for item in scored_rows[:5]
        if item.patent is not None
    ]

    all_analyzed_patents = [item.patent for item in scored_rows if item.patent is not None]

    project_notes = list(
        (
            await db.scalars(
                select(ProjectNote)
                .where(ProjectNote.project_id == project_id)
                .order_by(ProjectNote.created_at.desc())
            )
        ).all()
    )

    context: dict[str, Any] = {
        "project": project,
        "session": session,
        "top_5_results": top_5_results,
        "gap_analysis": gap_analysis,
        "project_notes": project_notes,
        "all_analyzed_patents": all_analyzed_patents,
        "feasibility_composite": _compute_feasibility_composite(gap_analysis),
        "report_generated_at": datetime.now(timezone.utc),
        "narrative_paragraphs": [line.strip() for line in gap_analysis.narrative_text.splitlines() if line.strip()],
    }
    return context


def render_report_html(context: dict[str, Any]) -> str:
    """Render report HTML from Jinja2 template and context data."""
    template = _jinja_env.get_template(_TEMPLATE_NAME)
    return template.render(**context)


async def generate_pdf_report(
    db: AsyncSession,
    project_id: UUID,
    session_id: UUID,
    user_id: UUID,
) -> bytes:
    """Generate a report PDF by assembling context, rendering HTML, and converting via WeasyPrint."""
    context = await build_report_context(db=db, project_id=project_id, session_id=session_id, user_id=user_id)
    html_content = render_report_html(context)

    pdf_bytes = await asyncio.to_thread(
        lambda: HTML(string=html_content).write_pdf()
    )
    return pdf_bytes
