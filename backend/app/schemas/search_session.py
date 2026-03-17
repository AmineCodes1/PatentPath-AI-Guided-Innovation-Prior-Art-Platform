"""Search session request and response schemas for CQL execution flows."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.search_session import SearchSessionStatus
from app.schemas.filters import DateRangeFilter, SearchFilters


class SearchRequest(BaseModel):
    """Request payload used to generate or execute a search query."""

    model_config = ConfigDict(from_attributes=True)

    query_text: str = Field(min_length=10)
    filters: DateRangeFilter | None = None
    country_codes: list[str] = Field(default_factory=list)
    ipc_classes: list[str] = Field(default_factory=list)
    applicant: str | None = None
    legal_status: str | None = None


class SearchSessionRead(BaseModel):
    """Search session details returned from search session endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    query_text: str
    cql_generated: str
    filters_json: dict[str, object] | SearchFilters
    result_count: int
    status: SearchSessionStatus
    executed_at: datetime
