"""Password hashing and JWT token utilities for authentication flows."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.schemas.user import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(plain: str) -> str:
    """Hash plain text passwords using bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify plain text password against stored hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict[str, object], expires_delta: timedelta | None = None) -> str:
    """Create signed JWT access token using configured secret and algorithm."""
    to_encode = dict(data)
    expire_at = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire_at
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenData:
    """Decode and validate JWT token and extract required claims."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id_raw = payload.get("sub")
        if not isinstance(user_id_raw, str):
            raise credentials_error
        return TokenData(user_id=UUID(user_id_raw))
    except (JWTError, ValueError) as exc:
        raise credentials_error from exc
