"""Async Redis client lifecycle and dependency helpers."""

from collections.abc import AsyncGenerator

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()
redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """Provide a request-scoped Redis client dependency."""
    yield redis_client


async def ping_redis() -> bool:
    """Check Redis server connectivity."""
    return await redis_client.ping()


async def close_redis() -> None:
    """Close Redis connections at shutdown."""
    await redis_client.aclose()
