"""Router exports for API version 1."""

from app.api.v1 import auth, health, patents, projects, reports, search

__all__ = ["auth", "health", "patents", "projects", "reports", "search"]
