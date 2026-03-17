"""Health-check endpoints for service and dependency status."""

from typing import Annotated

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import get_redis

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def get_health(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> dict[str, object]:
    """Return dependency health and current UTC timestamp."""
    db_connected = False
    redis_connected = False

    try:
        await db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    try:
        redis_connected = bool(await redis_client.ping())
    except Exception:
        redis_connected = False

    return {
        "status": "ok" if db_connected and redis_connected else "degraded",
        "db_connected": db_connected,
        "redis_connected": redis_connected,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
