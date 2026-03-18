"""Authentication endpoint and token utility tests."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import auth as auth_router
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token
from app.models.user import User


async def _fake_db_session():
    yield object()


def _build_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(auth_router.router, prefix="/api/v1")
    return test_app


def _make_user(email: str = "user@example.com") -> User:
    user = User(email=email, password_hash=str(uuid4()), display_name="Test User")
    user.id = uuid4()
    user.created_at = datetime.now(timezone.utc)
    return user


def test_register_login_and_me_flow(monkeypatch) -> None:
    user = _make_user()

    async def _create_user(_db, _payload):
        await asyncio.sleep(0)
        return user

    async def _authenticate_user(_db, email: str, password: str):
        await asyncio.sleep(0)
        return user

    async def _current_user_override():
        await asyncio.sleep(0)
        return user

    monkeypatch.setattr(auth_router, "create_user", _create_user)
    monkeypatch.setattr(auth_router, "authenticate_user", _authenticate_user)

    app = _build_test_app()
    app.dependency_overrides[get_db] = _fake_db_session
    app.dependency_overrides[get_current_user] = _current_user_override

    client = TestClient(app)

    register_resp = client.post(
        "/api/v1/auth/register",
        json={"email": user.email, "password": "password123", "display_name": user.display_name},
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["token_type"] == "bearer"

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]

    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == user.email

    app.dependency_overrides.clear()


def test_duplicate_email_returns_409(monkeypatch) -> None:
    async def _duplicate(_db, _payload):
        raise HTTPException(status_code=409, detail="Email already registered")

    monkeypatch.setattr(auth_router, "create_user", _duplicate)
    app = _build_test_app()
    app.dependency_overrides[get_db] = _fake_db_session

    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "password123", "display_name": "Dup"},
    )

    assert response.status_code == 409
    app.dependency_overrides.clear()


def test_invalid_password_returns_401(monkeypatch) -> None:
    async def _auth_none(_db, email: str, password: str):
        await asyncio.sleep(0)
        return None

    monkeypatch.setattr(auth_router, "authenticate_user", _auth_none)
    app = _build_test_app()
    app.dependency_overrides[get_db] = _fake_db_session

    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "badpassword"},
    )

    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_expired_token_returns_401() -> None:
    user_id = uuid4()
    expired_token = create_access_token({"sub": str(user_id)}, expires_delta=timedelta(seconds=-5))

    try:
        decode_access_token(expired_token)
        assert False, "Expected decode_access_token to raise HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401
