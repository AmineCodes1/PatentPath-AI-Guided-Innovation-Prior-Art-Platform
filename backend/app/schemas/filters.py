"""Reusable search filter schemas for PatentPath search endpoints."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class DateRangeFilter(BaseModel):
    """Date range filter used to bound patent publication dates."""

    model_config = ConfigDict(from_attributes=True)

    date_from: date | None = None
    date_to: date | None = None


class SearchFilters(BaseModel):
    """Normalized search filter object passed through API and services."""

    model_config = ConfigDict(from_attributes=True)

    date_from: date | None = None
    date_to: date | None = None
    country_codes: list[str] = Field(default_factory=list)
    ipc_classes: list[str] = Field(default_factory=list)
    applicant: str | None = None
    legal_status: str | None = None
