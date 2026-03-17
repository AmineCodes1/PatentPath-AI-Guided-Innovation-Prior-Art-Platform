"""Patent record response schemas for full and summarized result views."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatentRecordRead(BaseModel):
    """Complete patent record payload returned by patent detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    publication_number: str
    country_code: str
    title: str
    abstract: str
    claims: str | None
    description: str | None
    applicants: list[str]
    inventors: list[str]
    ipc_classes: list[str]
    cpc_classes: list[str]
    publication_date: date
    priority_date: date | None
    family_id: str | None
    legal_status: str | None
    espacenet_url: str
    cached_at: datetime
    cache_expires_at: datetime


class PatentRecordSummary(BaseModel):
    """Condensed patent payload used in search ranking responses."""

    model_config = ConfigDict(from_attributes=True)

    publication_number: str
    title: str
    abstract: str = Field(description="Abstract text truncated to 300 characters.")
    applicants: list[str]
    publication_date: date
    espacenet_url: str
    legal_status: str | None

    @field_validator("abstract", mode="before")
    @classmethod
    def truncate_abstract(cls, value: object) -> str:
        """Truncate abstracts to 300 chars for compact search result views."""
        text_value = str(value or "")
        return text_value if len(text_value) <= 300 else f"{text_value[:297]}..."
