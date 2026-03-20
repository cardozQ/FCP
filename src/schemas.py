from typing import Any, Dict, List, Literal, NewType, Optional, TypedDict

# ----------------------------------------
# CUSTOM TYPES
# ----------------------------------------

Url = NewType("Url", str)


# ----------------------------------------
# BASE RESPONSE TYPES
# ----------------------------------------

StatusType = Literal["success", "error"]


class BaseResponse(TypedDict, total=False):
    status: StatusType
    type: str
    data: Dict[str, Any]
    message: str


# ----------------------------------------
# SEARCH SCHEMAS
# ----------------------------------------


class SearchResult(TypedDict):
    title: str
    url: Url
    snippet: str


class SearchResponse(TypedDict):
    query: str
    results: List[SearchResult]


# ----------------------------------------
# EXTRACTED CONTENT SCHEMA
# ----------------------------------------


class ExtractedContent(TypedDict):
    title: str
    headings: List[str]
    content: str
    code_blocks: List[str]
    sections: List[Dict[str, str]]
    chunks: List[str]
    truncated: bool
    content_chars: int


# ----------------------------------------
# LINKS SCHEMA
# ----------------------------------------


class LinksResponse(TypedDict):
    links: List[Url]


# ----------------------------------------
# HISTORY SCHEMA
# ----------------------------------------


class HistoryResponse(TypedDict):
    history: List[Url]


# ----------------------------------------
# STATE SCHEMA
# ----------------------------------------


class StateData(TypedDict):
    current_url: Optional[Url]
    history: List[Url]
    visited_urls: List[Url]
    last_results: List[SearchResult]
    cached_content: Dict[Url, ExtractedContent]


# ----------------------------------------
# TOOL INPUT SCHEMAS
# ----------------------------------------


class SearchInput(TypedDict):
    query: str


class OpenInput(TypedDict):
    url: Url


class FindInput(TypedDict):
    text: str


class OpenResultInput(TypedDict):
    index: int


class ResearchInput(TypedDict):
    query: str
    result_index: int
    max_related_links: int


# ----------------------------------------
# CONTROLLER RESPONSE TYPES
# ----------------------------------------


class SearchOutput(BaseResponse):
    data: SearchResponse


class ContentOutput(BaseResponse):
    data: ExtractedContent


class LinksOutput(BaseResponse):
    data: LinksResponse


class HistoryOutput(BaseResponse):
    data: HistoryResponse


class ErrorOutput(BaseResponse):
    message: str
