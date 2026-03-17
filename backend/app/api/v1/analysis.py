"""Gap analysis API routes for triggering and fetching Claude-derived assessments."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.gap_analysis import GapAnalysis
from app.models.innovation_project import InnovationProject
from app.models.search_session import SearchSession
from app.schemas.gap_analysis import GapAnalysisRead
from app.worker.celery_app import celery_app

router = APIRouter(prefix="/analysis", tags=["analysis"])

auth_scheme = HTTPBearer(auto_error=False)


def require_auth_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(auth_scheme)],
) -> str:
    """Temporary auth guard requiring a Bearer token."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def _resolve_user_id_from_token(token: str) -> UUID:
    """Temporary user resolution until full JWT dependency is wired."""
    try:
        return UUID(token.strip())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token format",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def _ensure_owned_session(db: AsyncSession, session_id: UUID, user_id: UUID) -> SearchSession:
    session = await db.scalar(
        select(SearchSession)
        .join(InnovationProject, InnovationProject.id == SearchSession.project_id)
        .where(SearchSession.id == session_id, InnovationProject.user_id == user_id)
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search session not found")
    return session


@router.post("/session/{session_id}/gap-analysis")
async def trigger_gap_analysis(
    session_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> dict[str, str]:
    """Dispatch a background job to generate gap analysis for a session."""
    user_id = _resolve_user_id_from_token(token)
    await _ensure_owned_session(db=db, session_id=session_id, user_id=user_id)

    task = celery_app.send_task("run_gap_analysis_task", args=[str(session_id)])
    if task is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to dispatch analysis task")

    return {"job_id": task.id, "status": "PENDING"}


@router.get("/session/{session_id}/gap-analysis")
async def get_gap_analysis(
    session_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> GapAnalysisRead | dict[str, str]:
    """Return completed gap analysis payload or processing status."""
    user_id = _resolve_user_id_from_token(token)
    await _ensure_owned_session(db=db, session_id=session_id, user_id=user_id)

    analysis = await db.scalar(select(GapAnalysis).where(GapAnalysis.session_id == session_id))
    if analysis is None:
        return {"status": "PROCESSING"}

    return GapAnalysisRead.model_validate(analysis)


@router.get("/session/{session_id}/feasibility")
async def get_feasibility(
    session_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> dict[str, object]:
    """Return feasibility sub-scores and a composite percentage for a session."""
    user_id = _resolve_user_id_from_token(token)
    await _ensure_owned_session(db=db, session_id=session_id, user_id=user_id)

    analysis = await db.scalar(select(GapAnalysis).where(GapAnalysis.session_id == session_id))
    if analysis is None:
        return {"status": "PROCESSING"}

    scores = [
        analysis.feasibility_technical,
        analysis.feasibility_domain,
        analysis.feasibility_claim,
    ]
    numeric = [float(score) for score in scores if score is not None]
    composite_percentage = round((sum(numeric) / len(numeric)) * 20, 2) if numeric else 0.0

    return {
        "status": "COMPLETE",
        "session_id": str(session_id),
        "technical_readiness": analysis.feasibility_technical,
        "domain_specificity": analysis.feasibility_domain,
        "claim_potential": analysis.feasibility_claim,
        "composite_percentage": composite_percentage,
        "commentary": analysis.narrative_text[:300],
    }
