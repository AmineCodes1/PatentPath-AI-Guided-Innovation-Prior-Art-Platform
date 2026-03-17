"""Scored result ORM model storing ranking signals per search session and patent."""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.patent_record import PatentRecord
    from app.models.search_session import SearchSession


class RiskLabel(str, enum.Enum):
    """Risk buckets based on composite similarity score."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class ScoredResult(Base, UUIDPrimaryKeyMixin):
    """Per-session patent score breakdown and rank."""

    __tablename__ = "scored_results"
    __table_args__ = (UniqueConstraint("session_id", "patent_id", name="uq_scored_result_session_patent"),)

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("search_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patent_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bm25_score: Mapped[float] = mapped_column(Float, nullable=False)
    tfidf_cosine: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_cosine: Mapped[float] = mapped_column(Float, nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    risk_label: Mapped[RiskLabel] = mapped_column(
        Enum(RiskLabel, name="risk_label"),
        nullable=False,
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    session: Mapped[SearchSession] = relationship("SearchSession", back_populates="scored_results")
    patent: Mapped[PatentRecord] = relationship("PatentRecord", back_populates="scored_results")
