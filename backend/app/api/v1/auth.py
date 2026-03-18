"""Authentication API routes for PatentPath."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserRead
from app.services.user_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])
auth_scheme = HTTPBearer(auto_error=False)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
	payload: UserCreate,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
	"""Register a new user and return JWT token."""
	user = await create_user(db, payload)
	token = create_access_token({"sub": str(user.id)})
	return Token(access_token=token, token_type="bearer")


@router.post("/login")
async def login(
	payload: UserLogin,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
	"""Authenticate existing user credentials and return JWT token."""
	user = await authenticate_user(db, email=str(payload.email), password=payload.password)
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

	token = create_access_token({"sub": str(user.id)})
	return Token(access_token=token, token_type="bearer")


@router.get("/me")
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserRead:
	"""Return the currently authenticated user profile."""
	return UserRead.model_validate(current_user)


@router.post("/refresh")
async def refresh(
	credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(auth_scheme)],
) -> Token:
	"""Issue a new token from an existing valid bearer token."""
	if credentials is None or not credentials.credentials:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Authentication required",
			headers={"WWW-Authenticate": "Bearer"},
		)

	token_data = decode_access_token(credentials.credentials)
	new_token = create_access_token({"sub": str(token_data.user_id)})
	return Token(access_token=new_token, token_type="bearer")
