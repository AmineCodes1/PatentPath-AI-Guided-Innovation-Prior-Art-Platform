"""Redis-backed and in-memory fallback rate limiter for search execution endpoints."""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from collections.abc import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import redis.asyncio as redis

from app.core.redis_client import get_redis

MAX_SEARCHES_PER_HOUR = 10
WINDOW_SECONDS = 3600

_auth_scheme = HTTPBearer(auto_error=False)
_memory_lock = threading.Lock()
_memory_buckets: dict[str, list[float]] = defaultdict(list)


def _extract_subject(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials.strip()


def _prune_expired(timestamps: Iterable[float], now: float) -> list[float]:
    return [ts for ts in timestamps if now - ts < WINDOW_SECONDS]


def _raise_limited(retry_after_seconds: int) -> None:
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Search rate limit exceeded. Maximum 10 searches per hour.",
        headers={"Retry-After": str(max(1, retry_after_seconds))},
    )


async def _check_with_redis(subject: str, redis_client: redis.Redis) -> None:
    key = f"ratelimit:search:execute:{subject}"

    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, WINDOW_SECONDS)

    ttl = await redis_client.ttl(key)
    retry_after = ttl if ttl and ttl > 0 else WINDOW_SECONDS

    if count > MAX_SEARCHES_PER_HOUR:
        _raise_limited(retry_after_seconds=retry_after)


def _check_with_memory(subject: str) -> None:
    now = time.time()
    with _memory_lock:
        recent = _prune_expired(_memory_buckets[subject], now)
        if len(recent) >= MAX_SEARCHES_PER_HOUR:
            oldest = min(recent)
            retry_after = int(WINDOW_SECONDS - (now - oldest))
            _memory_buckets[subject] = recent
            _raise_limited(retry_after_seconds=retry_after)

        recent.append(now)
        _memory_buckets[subject] = recent


async def enforce_search_rate_limit(
    credentials: HTTPAuthorizationCredentials | None = Depends(_auth_scheme),
    redis_client: redis.Redis = Depends(get_redis),
) -> str:
    """Enforce max 10 search executions per authenticated subject per rolling hour."""
    subject = _extract_subject(credentials)

    try:
        await _check_with_redis(subject=subject, redis_client=redis_client)
    except HTTPException:
        raise
    except Exception:
        _check_with_memory(subject)

    return subject
