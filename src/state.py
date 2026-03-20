from typing import Dict, List, Optional

MAX_CACHE_SIZE = 20


class BrowserState:
    def __init__(self):
        self.current_url: Optional[str] = None
        self.history: List[str] = []
        self.visited_urls: set[str] = set()
        self.last_query: Optional[str] = None
        self.last_search_results: List[Dict] = []
        self.cache: Dict[str, Dict] = {}

    # ----------------------------
    # Navigation State
    # ----------------------------

    def set_current_url(self, url: str):
        if self.current_url:
            self.history.append(self.current_url)

        self.current_url = url
        self.visited_urls.add(url)

    def get_current_url(self) -> Optional[str]:
        return self.current_url

    def get_history(self) -> List[str]:
        return self.history[-10:]  # limit history size

    def has_visited(self, url: str) -> bool:
        return url in self.visited_urls

    # ----------------------------
    # Search State
    # ----------------------------

    def set_search_results(self, results: List[Dict]):
        self.last_search_results = results

    def set_last_results(self, results: List[Dict]):
        self.set_search_results(results)

    def set_last_query(self, query: str):
        self.last_query = query

    def get_last_query(self) -> Optional[str]:
        return self.last_query

    def get_search_results(self) -> List[Dict]:
        return self.last_search_results

    def get_last_results(self) -> List[Dict]:
        return self.get_search_results()

    def get_search_result(self, index: int) -> Optional[Dict]:
        if index < 0 or index >= len(self.last_search_results):
            return None
        return self.last_search_results[index]

    def add_to_history(self, url: str):
        self.history.append(url)

    # ----------------------------
    # Cache System (with limit)
    # ----------------------------

    def cache_content(self, url: str, content: Dict):
        if len(self.cache) >= MAX_CACHE_SIZE:
            # remove oldest inserted item
            self.cache.pop(next(iter(self.cache)))
        self.cache[url] = content

    def get_cached(self, url: str) -> Optional[Dict]:
        return self.cache.get(url)

    def get_cached_content(self, url: str) -> Optional[Dict]:
        return self.get_cached(url)

    # ----------------------------
    # Reset State
    # ----------------------------

    def reset(self):
        self.current_url = None
        self.history.clear()
        self.visited_urls.clear()
        self.last_query = None
        self.last_search_results = []
        self.cache.clear()


state = BrowserState()


class State(BrowserState):
    pass
