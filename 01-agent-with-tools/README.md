# Video 1 — IT Support Triage Agent

> **Series:** MAF Enterprise Series &nbsp;|&nbsp; **Concept:** Building your first agent with tools

An IT support triage agent that takes a plain-language problem description and automatically checks for open tickets, identifies the system owner, and recommends a priority level — all without any orchestration code.

---

## What it demonstrates

- Defining an **MAF Agent** with an LLM provider, instructions, and tools
- Writing **`@tool` functions** — plain Python with typed signatures and docstrings
- Wrapping the agent as an **MCP server** using FastMCP
- **Progress streaming** to MCP Inspector via `ctx.report_progress()`
- Swappable LLM providers — change from OpenAI to Azure or Anthropic without touching agent code

---

## Architecture

```
MCP Inspector          FastMCP Server         MAF Agent              Tools
    (client)              server.py             agent.py             tools.py

   message     ──►    triage_issue()   ──►   agent.run()   ──►  get_ticket_status
                                                            ──►  get_system_owner
                                                            ──►  get_priority_recommendation
   summary     ◄──    triage summary   ◄──   response.text
```

The MCP client only ever sees one tool: `triage_issue`. The MAF agent and its internal tools are hidden behind the MCP boundary — that clean separation is the point.

---

## Files

| File | Responsibility |
|------|----------------|
| `config.py` | Load env vars via pydantic-settings |
| `tools.py` | Three `@tool` functions — mock data with production API comments |
| `agent.py` | MAF Agent — client, instructions, tools |
| `server.py` | FastMCP server — exposes agent as `triage_issue` MCP tool |
| `scripts/run_direct.py` | Run the agent directly without MCP (dev/debug) |
| `tests/test_tools.py` | 15 unit tests — no API key needed |
| `tests/test_integration.py` | E2E agent tests — requires API key |
| `tests/test_mcp.py` | MCP server tests — in-memory + live round-trip |

---

## Setup

```bash
# From repo root
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY

uv sync
```

---

## Running

```bash
# Test the agent directly (no MCP)
python 01-agent-with-tools/scripts/run_direct.py

# Run the unit tests (no API key needed)
pytest 01-agent-with-tools/tests/test_tools.py -v

# Run all tests (API key required for integration + MCP tests)
pytest 01-agent-with-tools/tests/ -v

# Start the MCP server
python 01-agent-with-tools/server.py
# Server: http://localhost:8000/sse
```

---

## MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

- Transport: **SSE**
- URL: `http://localhost:8000/sse`
- Tool: `triage_issue`

**Example inputs:**

```
The HR portal is down and nobody can submit their timesheets. This is affecting the whole finance team.
```

```
Our VPN has been slow all morning. Remote workers across 3 offices are blocked from internal tools.
```

```
The customer analytics dashboard is throwing 500 errors since the deployment this morning.
```

Watch the **progress bar** advance in real time as the agent calls each tool — that is `ctx.report_progress()` streaming live.

---

## Swapping the LLM Provider

Change one import in `agent.py` — nothing else moves:

```python
# OpenAI (default)
from agent_framework.openai import OpenAIChatClient
client = OpenAIChatClient(model=..., api_key=...)

# Azure OpenAI
from agent_framework.azure import AzureOpenAIChatClient
client = AzureOpenAIChatClient(model=..., endpoint=..., api_key=...)

# Anthropic
from agent_framework.anthropic import AnthropicChatClient
client = AnthropicChatClient(model=..., api_key=...)
```

---

## Taking to Production

The tools in `tools.py` use mock data. Replace the comments marked `# Production:` with real API calls:

| Tool | Production integration |
|------|----------------------|
| `get_ticket_status` | ServiceNow / Jira API |
| `get_system_owner` | CMDB / service catalogue |
| `get_priority_recommendation` | CMDB criticality tier + priority matrix |
