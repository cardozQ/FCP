from typing import List, Optional
from urllib.parse import urljoin

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from src.state import state

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
    # Open Page (Improved)
    # ----------------------------

    def open_page(self, url: str) -> bool:
        try:
            self.launch()

            if not url.startswith("http"):
                url = "https://" + url

            # Navigate to page
            self.page.goto(url, timeout=DEFAULT_TIMEOUT)

            # 🔥 NEW: wait until DOM is loaded
            self.page.wait_for_load_state("domcontentloaded")

            state.set_current_url(url)

            return True

        except PlaywrightTimeoutError:
            print(f"[Timeout] Failed to load: {url}")
            return False

        except Exception as e:
            print(f"[Error] {e}")
            return False

    # ----------------------------
    # Get HTML
    # ----------------------------

    def get_html(self) -> Optional[str]:
        if not self.page:
            return None

        return self.page.content()

    # ----------------------------
    # Get Title
    # ----------------------------

    def get_title(self) -> Optional[str]:
        if not self.page:
            return None

        return self.page.title()

    # ----------------------------
    # Extract Links
    # ----------------------------

    def get_links(self) -> List[str]:
        if not self.page:
            return []

        links = self.page.eval_on_selector_all(
            "a", "elements => elements.map(el => el.href)"
        )

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
