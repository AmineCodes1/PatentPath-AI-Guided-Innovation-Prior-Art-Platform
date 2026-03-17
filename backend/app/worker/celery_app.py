"""Celery app configuration for asynchronous PatentPath jobs."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "patentpath",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.search_task"],
)

celery_app.autodiscover_tasks(["app.tasks"])
