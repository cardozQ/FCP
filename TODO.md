# Firefox MCP Server for Zed + Codex

Personal MCP server that allows Codex in Zed IDE to browse the web through Firefox with low token usage.

Goal:
Enable an autonomous research workflow where the model can search, open, extract, and navigate webpages efficiently.

---

# Phase 0 — Environment Setup

- [X] Install Python 3.11+
- [X] Create project repository
- [X] Create Python virtual environment
- [X] Activate virtual environment
- [X] Install dependencies
- [X] Install Playwright Firefox browser
- [X] Initialize pyproject.toml (uv)
- [X] Lock dependencies using uv.lock

Dependencies:

- fastmcp
- playwright
- beautifulsoup4
- requests
- readability-lxml

Commands:

pip install fastmcp playwright beautifulsoup4 requests readability-lxml
playwright install firefox

---

# Phase 1 — Project Structure

Create directory structure.

firefox-mcp/
│
├── src/
│   ├── server.py
│   ├── controller.py
│   ├── browser.py
│   ├── search.py
│   ├── extractor.py
│   ├── state.py
│   └── utils.py
│
├── config/
│   └── mcp.json
│
├── scripts/
│   └── start_firefox_debug.sh
│
├── docs/
│   └── architecture.md
│
├── logs/
│   └── mcp.log
│
└── TODO.md

Tasks:

- [X] Create directory structure
- [X] Create empty module files
- [X] Create logs directory
- [X] Initialize logging system

---

# Phase 2 — Core Architecture

Introduce a controller layer to orchestrate modules.

controller.py responsibilities:

- coordinate search
- coordinate browsing
- coordinate extraction
- manage state updates
- provide responses to MCP server

Tasks:

- [X] Implement controller.py
- [X] Connect search module
- [X] Connect browser module
- [X] Connect extractor module
- [X] Connect state module
- [X] Add structured response formatting

Architecture:

Codex → MCP → server.py → controller.py → modules

---

# Phase 2.5 — Interfaces & Contracts

Define clean interfaces between modules.

Tasks:

- [X] Define search result schema
- [X] Define extracted content schema
- [X] Define state structure
- [X] Define controller response format
- [X] Define MCP tool input/output schema

Example:

SearchResult:
{
  title: str
  url: str
  snippet: str
}

ExtractedContent:
{
  title: str
  headings: list[str]
  content: str
  code_blocks: list[str]
}

---

# Phase 3 — State Management

Maintain browser session state.

state.py responsibilities:

Track:

- current_url
- navigation history
- visited URLs
- last search results
- cached extracted content

Example state:

{
current_url,
history,
visited_urls,
last_results,
cached_content
}

Tasks:

- [X] Implement state manager
- [X] Track visited URLs
- [X] Track history
- [X] Store last search results
- [X] Implement simple content cache

---

# Phase 4 — Browser Automation Layer

Implement browser control using Playwright + Firefox.

browser.py responsibilities:

- launch Firefox
- open pages
- retrieve HTML
- extract links
- manage tabs

Functions:

open_page(url)

get_html()

get_title()

get_links()

close_browser()

Tasks:

- [X] Launch Firefox
- [X] Support headless mode
- [X] Support visible browser mode
- [X] Implement navigation
- [X] Retrieve page HTML
- [X] Extract links
- [X] Handle navigation timeout
- [X] Handle invalid URLs

---

# Phase 5 — Search Module

Implement web search using DuckDuckGo.

search.py responsibilities:

- query DuckDuckGo HTML endpoint
- parse search results
- return structured results

Return format:

{
title,
url,
snippet
}

Tasks:

- [X] Implement DuckDuckGo search
- [X] Parse results using BeautifulSoup
- [X] Return top 5 results
- [X] Handle empty search results
- [X] Add request timeout
- [X] Add retry mechanism

---

# Phase 6 — Content Extraction

Extract meaningful page content.

extractor.py responsibilities:

- remove navigation
- remove ads
- remove scripts
- extract main article
- extract headings
- preserve code blocks

Libraries:

- BeautifulSoup
- readability-lxml

Output format:

{
title,
headings,
content,
code_blocks
}

Tasks:

- [X] Implement readability extraction
- [X] Remove navigation bars
- [X] Remove scripts
- [X] Extract headings
- [X] Extract code blocks
- [X] Split content into chunks
- [X] Limit response size

---

# Phase 7 — Token Optimization

Reduce token usage for LLM responses.

Strategies:

- limit content size
- return structured sections
- avoid returning raw HTML
- implement content chunking

Tasks:

- [X] Implement MAX_CONTENT_CHARS guard
- [X] Implement response truncation
- [X] Implement section extraction
- [X] Implement caching of extracted content

Example constant:

MAX_CONTENT_CHARS = 8000

---

# Phase 8 — Utilities

Implement shared utilities.

utils.py responsibilities:

- rate limiting
- URL validation
- text truncation
- logging helpers

Tasks:

- [X] Implement rate limiter
- [X] Implement text truncation
- [X] Implement URL validator
- [X] Implement retry logic
- [X] Implement response formatting

---

# Phase 9 — MCP Server Implementation

Expose browser capabilities to Codex.

server.py responsibilities:

- register MCP server
- expose tools
- route requests to controller
- handle errors

MCP Tools:

web.search(query)

web.open(url)

web.extract()

web.links()

web.find(text)

web.history()

Tasks:

- [X] Implement MCP server
- [X] Register tools
- [X] Connect controller layer
- [X] Implement error handling

---

# Phase 10 — Logging System

Implement debugging logs.

Log file:

logs/mcp.log

Tasks:

- [X] Initialize logging
- [X] Log search queries
- [X] Log visited URLs
- [X] Log extraction size
- [X] Log tool usage
- [X] Log errors

---

# Phase 11 — Zed MCP Integration

Connect MCP server to Zed IDE.

config/mcp.json example:

{
"mcpServers": {
"firefox-web": {
"command": "python3",
"args": ["src/server.py"]
}
}
}

Tasks:

- [X] Create MCP configuration
- [X] Register MCP server
- [X] Restart Zed IDE
- [X] Test Codex tool usage

---

# Phase 12 — Autonomous Research Workflow

Enable agent-style browsing.

Agent workflow:

1. Search topic
2. Open relevant link
3. Extract article content
4. Identify important sections
5. Search inside page using web.find
6. Follow related links
7. Repeat until enough information is gathered

Tasks:

- [X] Design browsing strategy
- [X] Ensure structured responses
- [X] Enable multi-page exploration
- [X] Ensure minimal token usage

---

# Phase 13 — Advanced Features (Future)

Advanced browsing tools.

Tasks:

- [ ] Implement screenshot tool
- [ ] Implement scroll tool
- [ ] Implement multi-tab browsing
- [ ] Implement GitHub code extractor
- [ ] Implement documentation summarizer

Future MCP Tools:

web.screenshot()

web.scroll()

web.open_markdown()

github.search_code()

github.open_file()

---

# Phase 14 — Documentation

Write project documentation.

docs/architecture.md should include:

- MCP architecture
- browser automation workflow
- token optimization strategy
- agent browsing workflow
- system diagram

Tasks:

- [X] Write architecture documentation
- [X] Write installation guide
- [X] Write usage examples
- [X] Write developer guide

---

# Final Goal

Build a lightweight autonomous web research tool for Codex in Zed IDE.

Capabilities:

✔ Search the web  
✔ Open pages in Firefox  
✔ Extract articles  
✔ Navigate links  
✔ Analyze documentation  
✔ Perform autonomous research
