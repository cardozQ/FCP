"""Shared utilities for the Firefox MCP server."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "mcp.log"


def init_logging(
    log_path: Path | None = None, level: int = logging.INFO
) -> logging.Logger:
    """Initialize and return the project logger."""
    path = log_path or DEFAULT_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("firefox_mcp")
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("Logging initialized at %s", path)
    return logger
