"""MCP server entrypoint for Firefox web tools."""

from __future__ import annotations

import sys
from pathlib import Path

from fastmcp import FastMCP

if __package__:
    from .controller import Controller
    from .utils import init_logging
else:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.controller import Controller
    from src.utils import init_logging

logger = init_logging()
controller = Controller()
mcp = FastMCP(
    name="firefox-web",
    instructions="Search the web, open pages in Firefox, and extract page content.",
)


@mcp.tool(name="web.search", description="Search the web with DuckDuckGo.")
def web_search(query: str) -> dict:
    logger.info("Tool web.search called with query=%r", query)
    response = controller.search_web(query)
    logger.info("Tool web.search completed with status=%s", response["status"])
    return response


@mcp.tool(name="web.open", description="Open a URL in Firefox.")
def web_open(url: str) -> dict:
    logger.info("Tool web.open called with url=%s", url)
    response = controller.open_url(url)
    logger.info("Tool web.open completed with status=%s", response["status"])
    return response


@mcp.tool(
    name="web.open_result",
    description="Open a result from the most recent web.search by zero-based index.",
)
def web_open_result(index: int) -> dict:
    logger.info("Tool web.open_result called with index=%s", index)
    response = controller.open_search_result(index)
    logger.info("Tool web.open_result completed with status=%s", response["status"])
    return response


@mcp.tool(
    name="web.extract", description="Extract structured content from the current page."
)
def web_extract() -> dict:
    logger.info("Tool web.extract called")
    response = controller.extract_content()
    logger.info("Tool web.extract completed with status=%s", response["status"])
    return response


@mcp.tool(name="web.links", description="List links from the current page.")
def web_links() -> dict:
    logger.info("Tool web.links called")
    response = controller.get_links()
    logger.info("Tool web.links completed with status=%s", response["status"])
    return response


@mcp.tool(
    name="web.find", description="Find text occurrences in the current page HTML."
)
def web_find(text: str) -> dict:
    logger.info("Tool web.find called with text=%r", text)
    response = controller.find_in_page(text)
    logger.info("Tool web.find completed with status=%s", response["status"])
    return response


@mcp.tool(name="web.history", description="Return recent browsing history.")
def web_history() -> dict:
    logger.info("Tool web.history called")
    response = controller.get_history()
    logger.info("Tool web.history completed with status=%s", response["status"])
    return response


@mcp.tool(
    name="web.research",
    description="Search, open, extract, and suggest next links in one compact workflow.",
)
def web_research(query: str, result_index: int = 0, max_related_links: int = 5) -> dict:
    logger.info(
        "Tool web.research called with query=%r result_index=%s max_related_links=%s",
        query,
        result_index,
        max_related_links,
    )
    response = controller.research_topic(query, result_index, max_related_links)
    logger.info("Tool web.research completed with status=%s", response["status"])
    return response


def main() -> None:
    logger.info("Firefox MCP server starting.")
    mcp.run()


if __name__ == "__main__":
    main()
