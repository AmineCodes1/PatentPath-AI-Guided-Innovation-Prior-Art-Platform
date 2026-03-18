"""Celery task entrypoint for asynchronous patent preparation report generation."""

from __future__ import annotations

import asyncio
import base64
import logging
from uuid import UUID

from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.services.report_service import generate_pdf_report
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

_REPORT_TTL_SECONDS = 3600


async def _generate_report_async(project_id: str, session_id: str, user_id: str, job_id: str) -> dict[str, str]:
    async with SessionLocal() as db:
        pdf_bytes = await generate_pdf_report(
            db=db,
            project_id=UUID(project_id),
            session_id=UUID(session_id),
            user_id=UUID(user_id),
        )

    redis_key = f"report:pdf:{job_id}"
    encoded_payload = base64.b64encode(pdf_bytes).decode("ascii")
    await redis_client.set(redis_key, encoded_payload, ex=_REPORT_TTL_SECONDS)

    return {
        "job_id": job_id,
        "status": "READY",
        "redis_key": redis_key,
    }


@celery_app.task(bind=True, name="generate_report_task")
def generate_report_task(self, project_id: str, session_id: str, user_id: str) -> dict[str, str]:
    """Generate report PDF and cache artifact in Redis for temporary download."""
    try:
        return asyncio.run(
            _generate_report_async(
                project_id=project_id,
                session_id=session_id,
                user_id=user_id,
                job_id=self.request.id,
            )
        )
    except Exception as exc:
        logger.exception(
            "Report generation task failed for project %s session %s",
            project_id,
            session_id,
        )
        raise exc
