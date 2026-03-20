"""Shared utilities for the Firefox MCP server."""

from __future__ import annotations

import functools
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Dict, List, TypeVar
from urllib.parse import urlparse

DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "mcp.log"
MAX_CONTENT_CHARS = 8000
DEFAULT_CHUNK_SIZE = 1500
T = TypeVar("T")


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


class RateLimiter:
    """Very small in-process rate limiter."""

    def __init__(self, min_interval_seconds: float = 1.0):
        self.min_interval_seconds = min_interval_seconds
        self._last_called_at = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_called_at
        remaining = self.min_interval_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last_called_at = time.monotonic()


def retry(
    func: Callable[[], T],
    retries: int = 2,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    delay_seconds: float = 0.5,
) -> T:
    """Retry a callable a fixed number of times."""
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            return func()
        except exceptions as exc:
            last_error = exc
            if attempt >= retries:
                break
            time.sleep(delay_seconds)

    assert last_error is not None
    raise last_error


def with_retry(
    retries: int = 2,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    delay_seconds: float = 0.5,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator form of retry for simple synchronous functions."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return retry(
                lambda: func(*args, **kwargs),
                retries=retries,
                exceptions=exceptions,
                delay_seconds=delay_seconds,
            )

        return wrapper

    return decorator


def validate_url(url: str) -> bool:
    """Check that a URL uses http or https and has a network location."""
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def normalize_url(url: str) -> str:
    """Add a default https scheme when the URL omits one."""
    candidate = url.strip()
    if not candidate:
        return ""
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    return candidate


def format_response(
    status: str,
    *,
    type_: str | None = None,
    data: Dict[str, Any] | None = None,
    message: str | None = None,
) -> Dict[str, Any]:
    """Build a consistent response payload for controller/server paths."""
    response: Dict[str, Any] = {"status": status}
    if type_ is not None:
        response["type"] = type_
    if data is not None:
        response["data"] = data
    if message is not None:
        response["message"] = message
    return response


def normalize_text(text: str) -> str:
    """Collapse blank lines and trim surrounding whitespace."""
    lines = [line.strip() for line in text.splitlines()]
    filtered_lines: List[str] = []

    for line in lines:
        if line:
            filtered_lines.append(line)
            continue

        if filtered_lines and filtered_lines[-1] != "":
            filtered_lines.append("")

    return "\n".join(filtered_lines).strip()


def truncate_text(text: str, max_chars: int = MAX_CONTENT_CHARS) -> tuple[str, bool]:
    """Trim text to a maximum length while preserving whole-word boundaries when possible."""
    cleaned = normalize_text(text)
    if len(cleaned) <= max_chars:
        return cleaned, False

    truncated = cleaned[:max_chars].rsplit(" ", 1)[0].rstrip()
    if not truncated:
        truncated = cleaned[:max_chars].rstrip()

    return f"{truncated}...", True


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
    """Split text into moderately sized chunks for lower-token responses."""
    cleaned = normalize_text(text)
    if not cleaned:
        return []

    paragraphs = [
        paragraph.strip() for paragraph in cleaned.split("\n\n") if paragraph.strip()
    ]
    chunks: List[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        while len(paragraph) > chunk_size:
            split_at = paragraph.rfind(" ", 0, chunk_size)
            if split_at <= 0:
                split_at = chunk_size
            chunks.append(paragraph[:split_at].strip())
            paragraph = paragraph[split_at:].strip()

        current = paragraph

    if current:
        chunks.append(current)

    return chunks
