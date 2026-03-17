"""MCP server entrypoint for Firefox web tools."""

from __future__ import annotations

from utils import init_logging

logger = init_logging()


def main() -> None:
    """Start the MCP server process (implementation in later phases)."""
    logger.info("Firefox MCP server bootstrap initialized.")


if __name__ == "__main__":
    main()
