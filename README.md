# MAF Enterprise Series

Build production-ready AI agents from scratch using **Microsoft Agent Framework (MAF)**. One concept per video, from basics to production hardening.

Each video adds one layer: tools, memory, human oversight, observability, governance. By the end of the series you have a fully production-hardened agentic system.

---

## Videos

| # | Folder | Topic | Concepts |
|---|--------|-------|---------|
| 1 | [`01-agent-with-tools/`](01-agent-with-tools/) | IT Support Triage Agent | MAF basics, `@tool`, MCP server, progress streaming |
| 2 | _coming soon_ | Multi-turn Memory | `AgentSession`, conversation history |
| 3 | _coming soon_ | Observability | Logging, tracing, middleware |
| 4 | _coming soon_ | Human-in-the-Loop | HITL pause/resume |

---

## Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | [Microsoft Agent Framework (MAF)](https://github.com/microsoft/agent-framework) v1.2 |
| LLM Provider | OpenAI (swappable: Azure OpenAI, Anthropic, Ollama) |
| MCP Server | [FastMCP](https://github.com/jlowin/fastmcp) |
| MCP Client | [MCP Inspector](https://github.com/modelcontextprotocol/inspector) |
| Runtime | Python 3.11+ with [uv](https://github.com/astral-sh/uv) |

---

## Quick Start

```bash
git clone https://github.com/harinarayn/maf-enterprise-series.git
cd maf-enterprise-series

cp .env.example .env
# Add your OPENAI_API_KEY to .env

uv sync

# Video 1: run the agent directly
python 01-agent-with-tools/scripts/run_direct.py

# Video 1: start the MCP server, then open MCP Inspector
python 01-agent-with-tools/server.py
```

---

## Repository Structure

```
maf-enterprise-series/
├── 01-agent-with-tools/        # Video 1: IT Support Triage Agent
│   ├── agent.py                # MAF Agent definition
│   ├── tools.py                # The 3 @tool functions
│   ├── config.py               # Environment variable loading
│   ├── server.py               # FastMCP MCP server
│   ├── scripts/
│   │   └── run_direct.py       # Dev runner (no MCP needed)
│   └── tests/
│       ├── test_tools.py       # Unit tests (offline)
│       ├── test_integration.py # E2E agent tests
│       └── test_mcp.py         # MCP server tests
├── .env.example
└── pyproject.toml
```

---

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (`pip install uv`)
- [Node.js](https://nodejs.org/) for MCP Inspector (`npx`)
- An OpenAI API key with credits

---

## License

MIT
