from typing import Any, Dict

from .browser import Browser
from .extractor import Extractor
from .search import Search
from .state import State


class Controller:
    def __init__(self):
        self.state = State()
        self.browser = Browser()
        self.search = Search()
        self.extractor = Extractor()

    # -----------------------------
    # Helper: Standard Response
    # -----------------------------
    def _success(self, type_: str, data: Any) -> Dict[str, Any]:
        return {"status": "success", "type": type_, "data": data}

    def _error(self, message: str) -> Dict[str, Any]:
        return {"status": "error", "message": message}

    # -----------------------------
    # SEARCH
    # -----------------------------
    def search_web(self, query: str) -> Dict[str, Any]:
        if not query or not query.strip():
            return self._error("Query cannot be empty")

        try:
            results = self.search.search(query)

            if not results:
                return self._error("No results found")

            self.state.set_last_results(results)

            return self._success("search_results", {"query": query, "results": results})

        except Exception as e:
            return self._error(f"Search failed: {str(e)}")

    # -----------------------------
    # OPEN URL
    # -----------------------------
    def open_url(self, url: str) -> Dict[str, Any]:
        if not url or not url.startswith("http"):
            return self._error("Invalid URL")

        try:
            self.browser.open_page(url)

            title = self.browser.get_title()

            self.state.set_current_url(url)
            self.state.add_to_history(url)

            return self._success("page_opened", {"url": url, "title": title})

        except Exception as e:
            return self._error(f"Failed to open URL: {str(e)}")

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
