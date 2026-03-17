"""Async SQLAlchemy engine and session management utilities."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a request-scoped async database session."""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Verify database connectivity at startup."""
    async with engine.begin() as connection:
        await connection.run_sync(lambda _: None)


async def close_db() -> None:
    """Dispose engine resources during shutdown."""
    await engine.dispose()
