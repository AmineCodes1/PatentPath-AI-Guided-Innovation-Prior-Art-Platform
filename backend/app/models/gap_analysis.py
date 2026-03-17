"""Gap analysis ORM model containing AI-generated novelty risk outputs."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.search_session import SearchSession


class OverallRisk(str, enum.Enum):
    """Aggregate risk level for a search session gap analysis."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class GapAnalysis(Base, UUIDPrimaryKeyMixin):
    """Structured output from AI gap analysis for a completed search session."""

    __tablename__ = "gap_analyses"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("search_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    overall_risk: Mapped[OverallRisk] = mapped_column(
        Enum(OverallRisk, name="overall_risk"),
        nullable=False,
    )
    covered_aspects: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    gap_aspects: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    suggestions: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    narrative_text: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    feasibility_technical: Mapped[float | None] = mapped_column(Float, nullable=True)
    feasibility_domain: Mapped[float | None] = mapped_column(Float, nullable=True)
    feasibility_claim: Mapped[float | None] = mapped_column(Float, nullable=True)

    session: Mapped[SearchSession] = relationship("SearchSession", back_populates="gap_analysis")
