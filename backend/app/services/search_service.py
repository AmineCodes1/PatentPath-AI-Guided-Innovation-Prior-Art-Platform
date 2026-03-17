"""Search session result retrieval and analytics helpers."""

from __future__ import annotations

from collections import Counter
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.gap_analysis import GapAnalysis
from app.models.innovation_project import InnovationProject
from app.models.patent_record import PatentRecord
from app.models.scored_result import RiskLabel, ScoredResult
from app.models.search_session import SearchSession
from app.schemas.gap_analysis import GapAnalysisSummary
from app.schemas.scored_result import ScoredResultRead, SearchResultsResponse


async def _get_owned_session(db: AsyncSession, session_id: UUID, user_id: UUID) -> SearchSession:
    session = await db.scalar(
        select(SearchSession)
        .join(InnovationProject, InnovationProject.id == SearchSession.project_id)
        .where(SearchSession.id == session_id, InnovationProject.user_id == user_id)
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search session not found")
    return session


def _to_scored_result_read(result: ScoredResult) -> ScoredResultRead:
    return ScoredResultRead.model_validate(
        {
            "patent": result.patent,
            "bm25_score": result.bm25_score,
            "tfidf_cosine": result.tfidf_cosine,
            "semantic_cosine": result.semantic_cosine,
            "composite_score": result.composite_score,
            "risk_label": result.risk_label,
            "rank": result.rank,
        }
    )


def _to_gap_summary(gap: GapAnalysis | None) -> GapAnalysisSummary | None:
    if gap is None:
        return None
    return GapAnalysisSummary.model_validate(gap)


async def get_session_results(
    db: AsyncSession,
    session_id: UUID,
    user_id: UUID,
    page: int,
    per_page: int,
    risk_filter: list[RiskLabel] | None,
) -> SearchResultsResponse:
    """Return paginated scored results after validating session ownership."""
    await _get_owned_session(db=db, session_id=session_id, user_id=user_id)

    filters = [ScoredResult.session_id == session_id]
    if risk_filter:
        filters.append(ScoredResult.risk_label.in_(risk_filter))

    total_count = await db.scalar(select(func.count()).select_from(ScoredResult).where(*filters))
    total_count = int(total_count or 0)

    query = (
        select(ScoredResult)
        .where(*filters)
        .options(selectinload(ScoredResult.patent))
        .order_by(ScoredResult.rank.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    results = list((await db.scalars(query)).all())

    gap_analysis = await db.scalar(select(GapAnalysis).where(GapAnalysis.session_id == session_id))

    return SearchResultsResponse(
        session_id=session_id,
        total_count=total_count,
        results=[_to_scored_result_read(result) for result in results],
        gap_analysis=_to_gap_summary(gap_analysis),
    )


async def get_search_stats(db: AsyncSession, session_id: UUID, user_id: UUID) -> dict[str, object]:
    """Return aggregate statistics used by search result dashboards."""
    await _get_owned_session(db=db, session_id=session_id, user_id=user_id)

    rows = list(
        (
            await db.execute(
                select(ScoredResult, PatentRecord)
                .join(PatentRecord, PatentRecord.id == ScoredResult.patent_id)
                .where(ScoredResult.session_id == session_id)
            )
        ).all()
    )

    if not rows:
        return {
            "total_results": 0,
            "risk_distribution": {label.value: 0 for label in RiskLabel},
            "avg_composite_score": 0.0,
            "top_ipc_classes": [],
        }

    risk_counter: Counter[str] = Counter()
    ipc_counter: Counter[str] = Counter()
    composite_scores: list[float] = []

    for scored_result, patent in rows:
        risk_counter[scored_result.risk_label.value] += 1
        composite_scores.append(float(scored_result.composite_score))
        for ipc in patent.ipc_classes:
            if ipc:
                ipc_counter[str(ipc).strip().upper()] += 1

    risk_distribution = {label.value: int(risk_counter.get(label.value, 0)) for label in RiskLabel}
    avg_composite = round(sum(composite_scores) / len(composite_scores), 4)
    top_ipc_classes = [code for code, _ in ipc_counter.most_common(5)]

    return {
        "total_results": len(rows),
        "risk_distribution": risk_distribution,
        "avg_composite_score": avg_composite,
        "top_ipc_classes": top_ipc_classes,
    }
