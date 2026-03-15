# FCP
A playground for understanding how WebMCP orchestrates browser automation and search extraction.

## Motivation
I created this project to learn the plumbing behind WebMCP, from Codex driving MCP calls to Firefox responding with Playwright or remote debugging hooks.

## Workflow
1. Codex (inside Zed IDE) initiates a MCP tool call.
2. The Firefox MCP server receives that call and brokers Playwright/remote debugging sessions.
3. Mozilla Firefox 128.6.0 ESR executes the scripted interactions.
4. Web searches run inside the browser and pages are extracted via the MCP executor.

```
Codex (Zed IDE)
    │
    ├─> MCP Tool Call
    │
    ▼
Firefox MCP Server
    │
    ├─> Playwright / Remote Debugging
    │
    ▼
Mozilla Firefox 128.6.0 ESR
    │
    ▼
Web search + page extraction
```

## Project layout
```
firefox-mcp/
├── src/
│   ├── server.py         # HTTP entry point for MCP requests
│   ├── browser.py        # Browser lifecycle helpers
│   ├── extractor.py      # DOM extraction utilities
│   ├── search.py         # Search orchestration logic
│   └── utils.py          # Shared helpers and tooling
├── config/
│   └── mcp.json         # MCP runtime configuration
├── scripts/
│   └── start_firefox_debug.sh
├── docs/
│   └── architecture.md  # Design notes and diagrams
├── requirements.txt     # Python dependencies
└── TODO.md              # Next steps and learning tasks
```
