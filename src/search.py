"""DuckDuckGo HTML search integration."""

from __future__ import annotations

from typing import Dict, List
from urllib.parse import parse_qs, quote_plus, urlparse

import requests
from bs4 import BeautifulSoup

from .browser import Browser
from .utils import RateLimiter, retry

DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"
DEFAULT_TIMEOUT = 10
DEFAULT_RESULT_LIMIT = 5
DEFAULT_MAX_RETRIES = 2


class Search:
    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_results: int = DEFAULT_RESULT_LIMIT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.timeout = timeout
        self.max_results = max_results
        self.max_retries = max_retries
        self.rate_limiter = RateLimiter(min_interval_seconds=1.0)

    def search(self, query: str) -> List[Dict[str, str]]:
        if not query or not query.strip():
            return []

        html = self._fetch_results(query.strip())
        if not html:
            return []

        return self._parse_results(html)

    def _fetch_results(self, query: str) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

        def do_request() -> str:
            self.rate_limiter.wait()
            response = requests.get(
                DUCKDUCKGO_HTML_URL,
                params={"q": query},
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.text

        html = retry(
            do_request,
            retries=self.max_retries,
            exceptions=(requests.RequestException,),
            delay_seconds=1.0,
        )
        if self._is_anomaly_page(html):
            return self._fetch_results_with_browser(query)
        return html

    def _fetch_results_with_browser(self, query: str) -> str:
        browser = Browser(headless=True)
        try:
            opened = browser.open_page(
                f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            )
            if not opened:
                return ""
            return browser.get_html() or ""
        finally:
            browser.close_browser()

    def _is_anomaly_page(self, html: str) -> bool:
        lowered = html.lower()
        return "anomaly-modal" in lowered or "bots use duckduckgo too" in lowered

    def _parse_results(self, html: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        parsed_results: List[Dict[str, str]] = []

        for result in soup.select(".result"):
            title_node = result.select_one(".result__title a")
            snippet_node = result.select_one(".result__snippet")

            if not title_node:
                continue

            url = self._clean_result_url((title_node.get("href") or "").strip())
            title = title_node.get_text(" ", strip=True)
            snippet = snippet_node.get_text(" ", strip=True) if snippet_node else ""

            if not title or not url:
                continue

            parsed_results.append(
                {
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                }
            )

            if len(parsed_results) >= self.max_results:
                break

        return parsed_results

    def _clean_result_url(self, url: str) -> str:
        if not url:
            return ""
        if url.startswith("//"):
            url = f"https:{url}"

        parsed = urlparse(url)
        if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
            uddg = parse_qs(parsed.query).get("uddg", [""])[0]
            if uddg:
                return uddg

        return url
