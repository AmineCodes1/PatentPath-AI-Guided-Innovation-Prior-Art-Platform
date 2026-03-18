"""Report generation API routes for scheduling, status polling, and PDF download."""

from __future__ import annotations

import base64
from typing import Annotated
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.redis_client import redis_client
from app.schemas.report import ReportRequest, ReportStatusRead
from app.worker.celery_app import celery_app

router = APIRouter(prefix="/reports", tags=["reports"])

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


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_report(
    payload: ReportRequest,
    token: Annotated[str, Depends(require_auth_token)],
) -> dict[str, str]:
    """Dispatch a background report generation task for the given project/session."""
    user_id = _resolve_user_id_from_token(token)

    task = celery_app.send_task(
        "generate_report_task",
        args=[payload.project_id, payload.session_id, str(user_id)],
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to dispatch report task")

    return {"job_id": task.id, "status": "PENDING"}


@router.get("/status/{job_id}")
async def get_report_status(
    job_id: str,
    _: Annotated[str, Depends(require_auth_token)],
) -> ReportStatusRead:
    """Return report generation status and download URL when available."""
    task_result = AsyncResult(job_id, app=celery_app)

    if task_result.state in {"PENDING"}:
        return ReportStatusRead(job_id=job_id, status="PENDING")

    if task_result.state in {"STARTED", "RETRY"}:
        return ReportStatusRead(job_id=job_id, status="PROCESSING")

    if task_result.state == "FAILURE":
        return ReportStatusRead(job_id=job_id, status="FAILED")

    if task_result.state == "SUCCESS":
        return ReportStatusRead(
            job_id=job_id,
            status="READY",
            download_url=f"/api/v1/reports/download/{job_id}",
        )

    return ReportStatusRead(job_id=job_id, status="PROCESSING")


@router.get("/download/{job_id}")
async def download_report(
    job_id: str,
    _: Annotated[str, Depends(require_auth_token)],
) -> StreamingResponse:
    """Stream the generated PDF report for a completed job."""
    task_result = AsyncResult(job_id, app=celery_app)
    if task_result.state != "SUCCESS":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not ready")

    task_payload = task_result.result if isinstance(task_result.result, dict) else {}
    redis_key = str(task_payload.get("redis_key", ""))
    if not redis_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report artifact not found")

    encoded_pdf = await redis_client.get(redis_key)
    if not encoded_pdf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report expired or unavailable")

    try:
        pdf_bytes = base64.b64decode(encoded_pdf)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Corrupt report payload") from exc

    filename = f"patent_preparation_report_{job_id}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
