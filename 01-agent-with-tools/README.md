# Video 1: IT Support Triage Agent

**Series:** MAF Enterprise Series | **Concept:** Building your first agent with tools

An IT support triage agent that takes a plain-language problem description and automatically checks for open tickets, identifies the system owner, and recommends a priority level. No orchestration code required.

---

## What it demonstrates

- Defining an **MAF Agent** with an LLM provider, instructions, and tools
- Writing **`@tool` functions** (plain Python with typed signatures and docstrings)
- Wrapping the agent as an **MCP server** using FastMCP
- **Progress streaming** to MCP Inspector via `ctx.report_progress()`
- Swappable LLM providers: change from OpenAI to Azure or Anthropic without touching agent code

---

## Architecture

```
MCP Inspector          FastMCP Server         MAF Agent              Tools
    (client)              server.py             agent.py             tools.py

   message     -->    triage_issue()   -->   agent.run()   -->  get_ticket_status
                                                            -->  get_system_owner
                                                            -->  get_priority_recommendation
   summary     <--    triage summary   <--   response.text
```

The MCP client only ever sees one tool: `triage_issue`. The MAF agent and its internal tools are hidden behind the MCP boundary. That clean separation is the point.

---

## Files

| File | Responsibility |
|------|----------------|
| `config.py` | Load env vars via pydantic-settings |
| `tools.py` | Three `@tool` functions with mock data and production API comments |
| `agent.py` | MAF Agent: client, instructions, tools |
| `server.py` | FastMCP server that exposes the agent as the `triage_issue` MCP tool |
| `scripts/run_direct.py` | Run the agent directly without MCP (dev/debug) |
| `tests/test_tools.py` | 15 unit tests, no API key needed |
| `tests/test_integration.py` | E2E agent tests, requires API key |
| `tests/test_mcp.py` | MCP server tests: in-memory and live round-trip |

---

## Setup

```bash
# From repo root
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

uv sync
```

---

## Running

```bash
# Test the agent directly (no MCP)
python 01-agent-with-tools/scripts/run_direct.py

# Run unit tests (no API key needed)
pytest 01-agent-with-tools/tests/test_tools.py -v

# Run all tests (API key required for integration and MCP tests)
pytest 01-agent-with-tools/tests/ -v

# Start the MCP server
python 01-agent-with-tools/server.py
# Listening at: http://localhost:8000/sse
```

---

## MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

- Transport: **SSE**
- URL: `http://localhost:8000/sse`
- Tool: `triage_issue`

**Example inputs to try:**

```
The HR portal is down and nobody can submit their timesheets. This is affecting the whole finance team.
```

```
Our VPN has been slow all morning. Remote workers across 3 offices are blocked from internal tools.
```

```
The customer analytics dashboard is throwing 500 errors since the deployment this morning.
```

Watch the progress bar advance in real time as the agent calls each tool. That is `ctx.report_progress()` streaming live.

---

## Swapping the LLM Provider

Change one import in `agent.py` and nothing else moves:

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

The tools in `tools.py` use mock data. Replace the `# Production:` comments with real API calls:

| Tool | Production integration |
|------|----------------------|
| `get_ticket_status` | ServiceNow or Jira API |
| `get_system_owner` | CMDB or service catalogue |
| `get_priority_recommendation` | CMDB criticality tier with your priority matrix |
