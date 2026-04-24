"""Async SQLAlchemy engine and session management utilities."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a request-scoped async database session."""
    async with SessionLocal() as session:
        yield session


@asynccontextmanager
async def worker_session() -> AsyncIterator[AsyncSession]:
    """Create a fresh engine + session for Celery tasks to avoid event loop conflicts."""
    task_engine = create_async_engine(settings.database_url, pool_pre_ping=True, pool_size=1, max_overflow=0)
    task_session = async_sessionmaker(bind=task_engine, expire_on_commit=False, class_=AsyncSession)
    try:
        async with task_session() as session:
            yield session
    finally:
        await task_engine.dispose()


async def init_db() -> None:
    """Verify database connectivity at startup."""
    async with engine.begin() as connection:
        await connection.run_sync(lambda _: None)


async def close_db() -> None:
    """Dispose engine resources during shutdown."""
    await engine.dispose()
