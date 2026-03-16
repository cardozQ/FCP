I created this project to learn about how WebMCP functions :D

project Workflow 

High level overview 

Codex (inside Zed IDE)
        │
        │ MCP Tool Call
        ▼
Firefox MCP Server
        │
        │ Playwright / Remote Debugging
        ▼
Mozilla Firefox 128.6.0 ESR
        │
        ▼
Web search + page extraction

project structure :

firefox-mcp/
│
├── src/
│   ├── server.py
│   ├── browser.py
│   ├── extractor.py
│   ├── search.py
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
├── requirements.txt
└── TODO.md
