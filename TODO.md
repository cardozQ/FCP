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

- [ ] Implement controller.py
- [ ] Connect search module
- [ ] Connect browser module
- [ ] Connect extractor module
- [ ] Connect state module
- [ ] Add structured response formatting

Architecture:

Codex → MCP → server.py → controller.py → modules

---

# Phase 2.5 — Interfaces & Contracts

Define clean interfaces between modules.

Tasks:

- [ ] Define search result schema
- [ ] Define extracted content schema
- [ ] Define state structure
- [ ] Define controller response format
- [ ] Define MCP tool input/output schema

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

- [ ] Implement state manager
- [ ] Track visited URLs
- [ ] Track history
- [ ] Store last search results
- [ ] Implement simple content cache

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

- [ ] Launch Firefox
- [ ] Support headless mode
- [ ] Support visible browser mode
- [ ] Implement navigation
- [ ] Retrieve page HTML
- [ ] Extract links
- [ ] Handle navigation timeout
- [ ] Handle invalid URLs

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

- [ ] Implement DuckDuckGo search
- [ ] Parse results using BeautifulSoup
- [ ] Return top 5 results
- [ ] Handle empty search results
- [ ] Add request timeout
- [ ] Add retry mechanism

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

- [ ] Implement readability extraction
- [ ] Remove navigation bars
- [ ] Remove scripts
- [ ] Extract headings
- [ ] Extract code blocks
- [ ] Split content into chunks
- [ ] Limit response size

---

# Phase 7 — Token Optimization

Reduce token usage for LLM responses.

Strategies:

- limit content size
- return structured sections
- avoid returning raw HTML
- implement content chunking

Tasks:

- [ ] Implement MAX_CONTENT_CHARS guard
- [ ] Implement response truncation
- [ ] Implement section extraction
- [ ] Implement caching of extracted content

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

- [ ] Implement rate limiter
- [ ] Implement text truncation
- [ ] Implement URL validator
- [ ] Implement retry logic
- [ ] Implement response formatting

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

- [ ] Implement MCP server
- [ ] Register tools
- [ ] Connect controller layer
- [ ] Implement error handling

---

# Phase 10 — Logging System

Implement debugging logs.

Log file:

logs/mcp.log

Tasks:

- [ ] Initialize logging
- [ ] Log search queries
- [ ] Log visited URLs
- [ ] Log extraction size
- [ ] Log tool usage
- [ ] Log errors

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

- [ ] Create MCP configuration
- [ ] Register MCP server
- [ ] Restart Zed IDE
- [ ] Test Codex tool usage

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

- [ ] Design browsing strategy
- [ ] Ensure structured responses
- [ ] Enable multi-page exploration
- [ ] Ensure minimal token usage

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

- [ ] Write architecture documentation
- [ ] Write installation guide
- [ ] Write usage examples
- [ ] Write developer guide

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
