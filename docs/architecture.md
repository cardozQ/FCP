# Architecture

## Overview

This project exposes a small Firefox-backed web research tool over MCP so Codex in Zed can browse the web with structured, lower-token responses.

High-level flow:

```text
Codex in Zed
  -> MCP tool call
  -> FastMCP server (src/server.py)
  -> Controller (src/controller.py)
  -> Search / Browser / Extractor / State modules
  -> Structured response
```

## Main Components

### `src/server.py`

Responsibilities:

- create the `FastMCP` server
- register MCP tools
- route tool calls into the controller
- log tool usage

Registered tools:

- `web.search`
- `web.open`
- `web.open_result`
- `web.extract`
- `web.links`
- `web.find`
- `web.history`
- `web.research`

### `src/controller.py`

Responsibilities:

- validate inputs
- coordinate browser, search, extraction, and state
- return consistent success/error response payloads
- log important actions and failures

### `src/browser.py`

Responsibilities:

- launch Firefox with Playwright
- open pages
- retrieve current page HTML and title
- list page links
- manage a single browser/page session

### `src/search.py`

Responsibilities:

- fetch DuckDuckGo search results
- parse result title, URL, and snippet
- rate-limit and retry raw HTTP requests
- detect DuckDuckGo anti-bot challenge pages
- fall back to Firefox-based search page loading when direct requests are challenged

### `src/extractor.py`

Responsibilities:

- run `readability-lxml` on page HTML
- remove obvious non-content blocks
- extract headings and code blocks
- build structured sections
- truncate and chunk extracted content
- fall back to `article`, `main`, or `body` when readability output is too thin

### `src/state.py`

Responsibilities:

- track current URL
- store navigation history
- record visited URLs
- keep last search results
- cache extracted content

### `src/utils.py`

Responsibilities:

- logging initialization
- retry helpers
- in-process rate limiting
- URL normalization and validation
- response formatting
- text normalization, truncation, and chunking

## Browser Automation Workflow

Open flow:

1. `web.open(url)` reaches `server.py`
2. `server.py` calls `controller.open_url`
3. controller normalizes and validates the URL
4. `browser.py` launches Firefox if needed
5. Playwright opens the page and waits for DOM content loaded
6. title and state are updated
7. a structured success response is returned

## Search Workflow

1. `web.search(query)` reaches `controller.search_web`
2. `search.py` first tries a direct DuckDuckGo HTML request
3. if DuckDuckGo returns an anomaly / anti-bot page, `search.py` falls back to a Firefox-based fetch
4. result items are parsed into:

```json
{
  "title": "string",
  "url": "string",
  "snippet": "string"
}
```

5. controller stores the latest search results in state

`web.open_result(index)` can then open one of those stored search results without forcing the agent to repeat or manually copy URLs.

## Extraction Workflow

1. `web.extract()` uses the currently opened page HTML
2. extraction first checks the in-memory cache
3. HTML is passed through `readability-lxml`
4. noise blocks like nav, script, ads, popups, and sidebars are removed
5. headings, sections, code blocks, and normalized content are derived
6. the final content is truncated and chunked
7. extracted content is cached by URL

## Agent Browsing Workflow

Phase 12 adds a compact workflow tool for agent-style research.

`web.research(query, result_index=0, max_related_links=5)` performs:

1. search the topic
2. select and open one search result
3. extract the current page
4. return a compact page snapshot
5. suggest a small set of next links for continued exploration

The response is intentionally structured to keep token usage low while still giving the agent enough context to decide the next move.

Output shape includes:

```json
{
  "title": "string",
  "headings": ["..."],
  "content": "string",
  "code_blocks": ["..."],
  "sections": [{"title": "string", "content": "string"}],
  "chunks": ["..."],
  "truncated": false,
  "content_chars": 1234
}
```

## Token Optimization Strategy

Current token-saving behavior:

- avoid returning raw HTML
- limit extracted content to `MAX_CONTENT_CHARS = 8000`
- chunk large content into smaller sections
- return only top 5 search results
- return only the first 20 links from a page
- cache extracted content in memory to avoid repeated processing

## Zed Integration

Zed loads the server from the project-local [`.zed/settings.json`](/home/patrick/Experiments/FCP/.zed/settings.json#L1) using `context_servers`.

This is the active startup path:

```json
{
  "context_servers": {
    "firefox-web": {
      "command": "/home/patrick/Experiments/FCP/.venv/bin/python",
      "args": [
        "/home/patrick/Experiments/FCP/src/server.py"
      ]
    }
  }
}
```

## System Diagram

```text
Zed Agent / Codex
   |
   v
MCP Context Server: firefox-web
   |
   v
FastMCP Server (src/server.py)
   |
   v
Controller (src/controller.py)
   |         |         |         |
   v         v         v         v
Search    Browser   Extractor   State
   |         |
   v         v
DuckDuckGo   Firefox / Playwright
```

## Developer Notes

- The search backend is sensitive to DuckDuckGo bot detection; the browser fallback is what keeps search working reliably here.
- Logging writes to `logs/mcp.log`.
- The current browser layer manages one active page, not multiple tabs.
- State and extraction cache are in-memory only.
