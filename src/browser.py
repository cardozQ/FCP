from typing import List, Optional
from urllib.parse import urljoin

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from src.state import state
from src.utils import normalize_url, validate_url

DEFAULT_TIMEOUT = 10000  # 10 seconds


class Browser:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    # ----------------------------
    # Launch Browser
    # ----------------------------

    def launch(self):
        if self.browser:
            return

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(headless=self.headless)
        self.page = self.browser.new_page()

    # ----------------------------
    # Open Page (Improved Errors)
    # ----------------------------

    def open_page(self, url: str) -> bool:
        try:
            self.launch()

            url = normalize_url(url)
            if not validate_url(url):
                return False

            self.page.goto(url, timeout=DEFAULT_TIMEOUT)
            self.page.wait_for_load_state("domcontentloaded")

            state.set_current_url(url)

            return True

        except PlaywrightTimeoutError:
            print(f"[Timeout] Failed to load: {url}")
            return False

        except Exception:
            print(f"[Error] Failed to open {url}")
            return False

    # ----------------------------
    # Get HTML (Safe)
    # ----------------------------

    def get_html(self) -> Optional[str]:
        if not self.page:
            return None

        try:
            return self.page.content()
        except Exception:
            return None

    # ----------------------------
    # Get Title (Safe)
    # ----------------------------

    def get_title(self) -> Optional[str]:
        if not self.page:
            return None

        try:
            return self.page.title()
        except Exception:
            return None

    # ----------------------------
    # Extract Links
    # ----------------------------

    def get_links(self) -> List[str]:
        if not self.page:
            return []

        try:
            links = self.page.eval_on_selector_all(
                "a", "elements => elements.map(el => el.href)"
            )
        except Exception:
            return []

        cleaned_links = []
        base_url = state.get_current_url()

        for link in links:
            if not link:
                continue

            full_url = urljoin(base_url, link)

            if full_url.startswith("http"):
                cleaned_links.append(full_url)

        return list(set(cleaned_links))

    # ----------------------------
    # Close Browser
    # ----------------------------

    def close_browser(self):
        if self.browser:
            self.browser.close()
            self.playwright.stop()
            self.browser = None
            self.page = None


browser = Browser()
