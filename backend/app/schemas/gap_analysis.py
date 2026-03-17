"""Gap analysis schemas for AI novelty risk summaries and full narrative output."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.gap_analysis import OverallRisk


class GapAnalysisRead(BaseModel):
    """Complete gap analysis object returned by analysis endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    overall_risk: OverallRisk
    covered_aspects: list[str]
    gap_aspects: list[str]
    suggestions: list[str]
    narrative_text: str
    model_used: str
    generated_at: datetime
    feasibility_technical: float | None = None
    feasibility_domain: float | None = None
    feasibility_claim: float | None = None


class GapAnalysisSummary(BaseModel):
    """Compact gap analysis payload embedded in search results responses."""

    model_config = ConfigDict(from_attributes=True)

    overall_risk: OverallRisk
    covered_aspects: list[str]
    gap_aspects_count: int = 0
    suggestions_count: int = 0
    feasibility_score: float = 0.0
    feasibility_technical: float | None = None
    feasibility_domain: float | None = None
    feasibility_claim: float | None = None

    @model_validator(mode="before")
    @classmethod
    def derive_summary_fields(cls, value: object) -> object:
        """Populate count and feasibility fields from detailed model-like inputs."""
        if isinstance(value, dict):
            payload = dict(value)
            gap_aspects = payload.get("gap_aspects") or []
            suggestions = payload.get("suggestions") or []
            payload["gap_aspects_count"] = len(gap_aspects)
            payload["suggestions_count"] = len(suggestions)
            sub_scores = [
                payload.get("feasibility_technical"),
                payload.get("feasibility_domain"),
                payload.get("feasibility_claim"),
            ]
            numeric_scores = [float(score) for score in sub_scores if score is not None]
            payload["feasibility_score"] = (
                sum(numeric_scores) / len(numeric_scores) if numeric_scores else 0.0
            )
            return payload
        return value
