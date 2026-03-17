"""Patent record ORM model storing cached bibliographic and text content from OPS."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.scored_result import ScoredResult

JSONB_EMPTY_ARRAY_DEFAULT = text("'[]'::jsonb")


class PatentRecord(Base, UUIDPrimaryKeyMixin):
    """Cached patent publication record and enrichment fields."""

    __tablename__ = "patent_records"

    publication_number: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    claims: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    applicants: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=JSONB_EMPTY_ARRAY_DEFAULT,
    )
    inventors: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=JSONB_EMPTY_ARRAY_DEFAULT,
    )
    ipc_classes: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=JSONB_EMPTY_ARRAY_DEFAULT,
    )
    cpc_classes: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=JSONB_EMPTY_ARRAY_DEFAULT,
    )
    publication_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    family_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    legal_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    espacenet_url: Mapped[str] = mapped_column(Text, nullable=False)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    cache_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    scored_results: Mapped[list[ScoredResult]] = relationship(
        "ScoredResult",
        back_populates="patent",
        cascade="all, delete-orphan",
    )
