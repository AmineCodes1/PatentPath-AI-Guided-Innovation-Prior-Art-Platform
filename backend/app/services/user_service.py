"""User service operations for registration and credential validation."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    """Create a new user if email is unique."""
    existing = await db.scalar(select(User).where(User.email == str(user_create.email).lower()))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=str(user_create.email).lower(),
        password_hash=hash_password(user_create.password),
        display_name=user_create.display_name.strip(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Validate user credentials and return matching user on success."""
    user = await db.scalar(select(User).where(User.email == email.lower().strip()))
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Fetch user by UUID primary key."""
    return await db.scalar(select(User).where(User.id == user_id))
