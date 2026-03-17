"""Scored result schemas for ranked patent search responses."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.scored_result import RiskLabel
from app.schemas.gap_analysis import GapAnalysisSummary
from app.schemas.patent_record import PatentRecordSummary


class ScoredResultRead(BaseModel):
    """Scored patent result with component scores and rank."""

    model_config = ConfigDict(from_attributes=True)

    patent: PatentRecordSummary
    bm25_score: float
    tfidf_cosine: float
    semantic_cosine: float
    composite_score: float
    risk_label: RiskLabel
    rank: int


class ScoredResultCreate(BaseModel):
    """Internal payload schema used before persisting scored results."""

    model_config = ConfigDict(from_attributes=True)

    patent_id: UUID
    bm25_score: float
    tfidf_cosine: float
    semantic_cosine: float
    composite_score: float
    risk_label: RiskLabel
    rank: int


class SearchResultsResponse(BaseModel):
    """Paginated results payload returned by search result endpoints."""

    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    total_count: int
    results: list[ScoredResultRead]
    gap_analysis: GapAnalysisSummary | None = None
