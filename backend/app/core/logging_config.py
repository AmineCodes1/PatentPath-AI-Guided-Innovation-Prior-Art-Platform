"""Structured JSON logging configuration for backend services."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any


class JsonLogFormatter(logging.Formatter):
    """Format log records as structured JSON objects."""

    RESERVED = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
    }

    def format(self, record: logging.LogRecord) -> str:
        extra_fields: dict[str, Any] = {}
        for key, value in record.__dict__.items():
            if key not in self.RESERVED:
                extra_fields[key] = value

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
            "extra_fields": extra_fields,
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    """Initialize root logger and service-specific levels once."""
    root_logger = logging.getLogger()
    if getattr(root_logger, "_patentpath_logging_configured", False):
        return

    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    logging.getLogger("app.services.nlp").setLevel(logging.DEBUG)
    logging.getLogger("app.api").setLevel(logging.INFO)
    logging.getLogger("app.services.ops_connector").setLevel(logging.WARNING)

    root_logger._patentpath_logging_configured = True  # type: ignore[attr-defined]
