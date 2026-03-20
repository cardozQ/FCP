# Firefox MCP Server for Zed + Codex

Lightweight MCP server that lets Codex in Zed browse the web through Firefox with lower-token responses.

## What It Can Do

- Search the web with DuckDuckGo
- Open pages in Firefox through Playwright
- Extract structured page content
- List page links
- Search text inside the current page
- Track simple browsing history

## Project Layout

```text
src/
  server.py       FastMCP server and tool registration
  controller.py   Orchestrates browser, search, extraction, and state
  browser.py      Firefox / Playwright automation
  search.py       DuckDuckGo search with browser fallback
  extractor.py    Readability + BeautifulSoup extraction
  state.py        Session state and extraction cache
  utils.py        Logging, retry, URL helpers, truncation, chunking
docs/
  architecture.md
.zed/
  settings.json   Project-local Zed MCP server registration
```

## Requirements

- Python 3.11+
- `uv`
- Firefox installed for Playwright
- Zed with Agent / MCP support enabled

## Setup

```bash
uv venv
source .venv/bin/activate
uv sync
playwright install firefox
```

## Run The Server Manually

```bash
.venv/bin/python src/server.py
```

The server uses stdio transport and writes logs to `logs/mcp.log`.

## Use It In Zed

This project already contains a project-local Zed config in [`.zed/settings.json`](/home/patrick/Experiments/FCP/.zed/settings.json#L1).

Current server config:

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

Steps:

1. Open this project folder in Zed.
2. Trust the workspace if prompted.
3. Restart Zed or reload the window.
4. Open the Agent settings or MCP/context server view.
5. Confirm `firefox-web` appears and is running.

## Available MCP Tools

- `web.search(query)`
- `web.open(url)`
- `web.open_result(index)`
- `web.extract()`
- `web.links()`
- `web.find(text)`
- `web.history()`
- `web.research(query, result_index=0, max_related_links=5)`

## Example Workflow

1. `web.search("OpenAI")`
2. `web.open_result(0)`
3. `web.extract()`
4. `web.find("GPT-5")`
5. `web.links()`

Compact workflow:

1. `web.research("OpenAI")`
2. inspect `page_snapshot`
3. choose a URL from `related_links`
4. `web.open(url)` to continue exploration

## Notes

- Search uses DuckDuckGo HTML search.
- If DuckDuckGo returns an anti-bot challenge to raw HTTP requests, the search module falls back to Firefox-based page fetches.
- Extracted content is truncated and chunked for lower token usage.
- Cached extraction results are stored in process memory.
- Phase 12 adds a compact research workflow for agent-style browsing.

## Logs

Main log file:

```text
logs/mcp.log
```

The log currently records:

- tool usage
- search queries
- visited URLs
- extraction size
- errors

## Current Status

Completed:

- Phase 0 through Phase 12

Remaining:

- Phase 13
- Phase 14 documentation can still be expanded further, but core project docs are now in place
