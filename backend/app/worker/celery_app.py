"""Celery app configuration for asynchronous PatentPath jobs."""

from celery import Celery

celery_app = Celery(
    "patentpath",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
)
