"""Logging helpers for backend observability."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """Format log records as compact JSON payloads."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "event_data"):
            payload["event_data"] = record.event_data
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure application logging once for API and pipeline components."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def log_event(logger: logging.Logger, message: str, **event_data: Any) -> None:
    """Emit a structured info log with contextual fields."""
    logger.info(message, extra={"event_data": event_data})
