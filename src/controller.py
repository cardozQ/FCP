from typing import Any, Dict, List

from .browser import Browser
from .extractor import Extractor
from .search import Search
from .state import state
from .utils import format_response, init_logging, normalize_url, validate_url

logger = init_logging()


class Controller:
    def __init__(self):
        self.state = state
        self.browser = Browser()
        self.search = Search()
        self.extractor = Extractor()

    # -----------------------------
    # Helper: Standard Response
    # -----------------------------
    def _success(self, type_: str, data: Any) -> Dict[str, Any]:
        return format_response("success", type_=type_, data=data)

    def _error(self, message: str) -> Dict[str, Any]:
        logger.error(message)
        return format_response("error", message=message)

    # -----------------------------
    # SEARCH
    # -----------------------------
    def search_web(self, query: str) -> Dict[str, Any]:
        if not query or not query.strip():
            return self._error("Query cannot be empty")

        try:
            logger.info("Search query received: %s", query)
            results = self.search.search(query)

            if not results:
                return self._error("No results found")

            self.state.set_last_query(query)
            self.state.set_last_results(results)

            return self._success(
                "search_results",
                {
                    "query": query,
                    "results": results,
                    "next_actions": [
                        "Use web.open_result(index) to open a search result.",
                        "Use web.research(query) for a compact research workflow.",
                    ],
                },
            )

        except Exception as e:
            return self._error(f"Search failed: {str(e)}")

    # -----------------------------
    # OPEN URL
    # -----------------------------
    def open_url(self, url: str) -> Dict[str, Any]:
        normalized_url = normalize_url(url)
        if not validate_url(normalized_url):
            return self._error("Invalid URL")

        try:
            opened = self.browser.open_page(normalized_url)
            if not opened:
                return self._error("Browser failed to open URL")

            title = self.browser.get_title()

            self.state.set_current_url(normalized_url)
            logger.info("Visited URL: %s", normalized_url)

            return self._success("page_opened", {"url": normalized_url, "title": title})

        except Exception as e:
            return self._error(f"Failed to open URL: {str(e)}")

    def open_search_result(self, index: int) -> Dict[str, Any]:
        try:
            result = self.state.get_search_result(index)
            if result is None:
                return self._error("Search result index out of range")

            response = self.open_url(result["url"])
            if response["status"] == "error":
                return response

            response["data"]["selected_result"] = {
                "index": index,
                "title": result["title"],
                "url": result["url"],
                "snippet": result["snippet"],
            }
            return response
        except Exception as e:
            return self._error(f"Failed to open search result: {str(e)}")

    # -----------------------------
    # EXTRACT CONTENT
    # -----------------------------
    def extract_content(self) -> Dict[str, Any]:
        current_url = self.state.get_current_url()

        if not current_url:
            return self._error("No page is currently open")

        try:
            # Check cache first (performance boost)
            cached = self.state.get_cached_content(current_url)
            if cached:
                return self._success("content_cached", cached)

            html = self.browser.get_html()

            if not html:
                return self._error("Failed to retrieve page HTML")

            extracted = self.extractor.extract(html)

            self.state.cache_content(current_url, extracted)
            logger.info(
                "Extraction size for %s: %s chars",
                current_url,
                extracted.get("content_chars", 0),
            )

            return self._success("content", extracted)

        except Exception as e:
            return self._error(f"Extraction failed: {str(e)}")

    # -----------------------------
    # GET LINKS
    # -----------------------------
    def get_links(self) -> Dict[str, Any]:
        try:
            links = self.browser.get_links()

            if not links:
                return self._error("No links found")

            return self._success(
                "links",
                {
                    "links": links[:20]  # token safety
                },
            )

        except Exception as e:
            return self._error(f"Failed to get links: {str(e)}")

    def research_topic(
        self, query: str, result_index: int = 0, max_related_links: int = 5
    ) -> Dict[str, Any]:
        if not query or not query.strip():
            return self._error("Query cannot be empty")

        cached_query = self.state.get_last_query()
        results: List[Dict[str, Any]]

        if cached_query == query and self.state.get_last_results():
            results = self.state.get_last_results()
        else:
            search_response = self.search_web(query)
            if search_response["status"] == "error":
                return search_response
            results = search_response["data"]["results"]

        if result_index < 0 or result_index >= len(results):
            return self._error("Selected result index is out of range")

        open_response = self.open_search_result(result_index)
        if open_response["status"] == "error":
            return open_response

        extract_response = self.extract_content()
        if extract_response["status"] == "error":
            return extract_response

        links_response = self.get_links()
        links: List[str] = []
        if links_response["status"] == "success":
            links = links_response["data"]["links"][:max_related_links]

        extracted = extract_response["data"]
        related_links = [
            {"url": link, "visited": self.state.has_visited(link)} for link in links
        ]

        return self._success(
            "research_brief",
            {
                "query": query,
                "selected_result": {
                    "index": result_index,
                    "title": results[result_index]["title"],
                    "url": results[result_index]["url"],
                    "snippet": results[result_index]["snippet"],
                },
                "search_results": [
                    {
                        "index": idx,
                        "title": result["title"],
                        "url": result["url"],
                        "snippet": result["snippet"],
                    }
                    for idx, result in enumerate(results)
                ],
                "page_snapshot": {
                    "title": extracted.get("title", ""),
                    "headings": extracted.get("headings", [])[:5],
                    "summary": extracted.get("chunks", [])[:2],
                    "sections": extracted.get("sections", [])[:4],
                    "truncated": extracted.get("truncated", False),
                },
                "related_links": related_links,
                "next_actions": [
                    "Use web.open(url) on a related link to continue exploration.",
                    "Use web.find(text) to inspect a keyword on the current page.",
                    "Use web.history() to review visited pages.",
                ],
            },
        )

    # -----------------------------
    # FIND IN PAGE
    # -----------------------------
    def find_in_page(self, text: str) -> Dict[str, Any]:
        if not text:
            return self._error("Search text cannot be empty")

        try:
            html = self.browser.get_html()

            if not html:
                return self._error("No page content available")

            matches = html.lower().count(text.lower())

            return self._success("search_in_page", {"query": text, "matches": matches})

        except Exception as e:
            return self._error(f"Search in page failed: {str(e)}")

    # -----------------------------
    # HISTORY
    # -----------------------------
    def get_history(self) -> Dict[str, Any]:
        try:
            history = self.state.get_history()

            return self._success("history", {"history": history})

        except Exception as e:
            return self._error(f"Failed to retrieve history: {str(e)}")
