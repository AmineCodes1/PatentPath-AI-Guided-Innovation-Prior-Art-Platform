"""Celery task entrypoint for Claude-powered gap analysis generation."""

from __future__ import annotations

import asyncio
import logging

from app.core.database import SessionLocal
from app.services.gap_analysis_service import run_gap_analysis
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _run_gap_analysis_async(session_id: str) -> dict[str, object]:
    async with SessionLocal() as db:
        analysis = await run_gap_analysis(db=db, session_id=session_id)
        return {
            "session_id": session_id,
            "status": "COMPLETE",
            "gap_analysis_id": str(analysis.id),
        }


@celery_app.task(name="run_gap_analysis_task")
def run_gap_analysis_task(session_id: str) -> dict[str, object]:
    """Run gap analysis for a search session in a Celery worker process."""
    try:
        return asyncio.run(_run_gap_analysis_async(session_id=session_id))
    except Exception as exc:
        logger.exception("Gap analysis task failed for session %s", session_id)
        raise exc
