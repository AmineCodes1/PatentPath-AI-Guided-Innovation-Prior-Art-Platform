"""User and authentication payload schemas for PatentPath."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Registration payload for creating a new user account."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)


class UserRead(BaseModel):
    """Public user profile data returned by auth endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    display_name: str
    created_at: datetime


class UserLogin(BaseModel):
    """Credential payload used to request an access token."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    """JWT access token response payload."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token claims required for authenticated operations."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
