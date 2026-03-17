"""Report generation request and async job status schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ReportRequest(BaseModel):
    """Request payload to generate a patent preparation report."""

    model_config = ConfigDict(from_attributes=True)

    project_id: str
    session_id: str


class ReportStatusRead(BaseModel):
    """Report job status payload used by polling endpoints."""

    model_config = ConfigDict(from_attributes=True)

    job_id: str
    status: str
    download_url: str | None = None
