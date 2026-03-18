"""Test configuration and environment defaults for backend test suite."""

from __future__ import annotations

import os


os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/patentpath_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
