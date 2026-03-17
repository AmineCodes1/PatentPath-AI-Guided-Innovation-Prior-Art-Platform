"""Search session ORM model for executed CQL searches and processing state."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.gap_analysis import GapAnalysis
    from app.models.innovation_project import InnovationProject
    from app.models.scored_result import ScoredResult


class SearchSessionStatus(str, enum.Enum):
    """Processing states for prior art search execution."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class SearchSession(Base, UUIDPrimaryKeyMixin):
    """Search execution metadata and resulting status for one query run."""

    __tablename__ = "search_sessions"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("innovation_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    cql_generated: Mapped[str] = mapped_column(Text, nullable=False)
    filters_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    status: Mapped[SearchSessionStatus] = mapped_column(
        Enum(SearchSessionStatus, name="search_session_status"),
        nullable=False,
        default=SearchSessionStatus.PENDING,
        server_default=SearchSessionStatus.PENDING.value,
    )
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    project: Mapped[InnovationProject] = relationship("InnovationProject", back_populates="search_sessions")
    scored_results: Mapped[list[ScoredResult]] = relationship(
        "ScoredResult",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    gap_analysis: Mapped[GapAnalysis | None] = relationship(
        "GapAnalysis",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
