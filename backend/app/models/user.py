"""User ORM model representing authenticated PatentPath users."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.innovation_project import InnovationProject


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Application user with credentials and profile metadata."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    epo_consumer_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Store encrypted at the application layer.",
    )

    projects: Mapped[list[InnovationProject]] = relationship(
        "InnovationProject",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
