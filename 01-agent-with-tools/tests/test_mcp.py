# tests/test_mcp.py
# ──────────────────────────────────────────────────────────────
# MCP end-to-end tests — calls the FastMCP server in-memory,
# exactly as MCP Inspector would, but without starting HTTP.
#
# The in-memory client bypasses networking so tests are fast
# and reliable in CI. The server code path (triage_issue tool,
# agent.run, response.text) is fully exercised.
# ──────────────────────────────────────────────────────────────

import pytest
from fastmcp import Client

# Import the live mcp instance from server.py.
# This also creates the MAF agent once, matching production behaviour.
from server import mcp


@pytest.mark.asyncio
async def test_triage_issue_tool_is_registered():
    # Verify MCP Inspector would see the tool before making any LLM calls.
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        assert "triage_issue" in tool_names


@pytest.mark.asyncio
async def test_triage_issue_returns_text_response():
    # Full round-trip: MCP client → triage_issue → MAF agent → OpenAI → tools → reply.
    async with Client(mcp) as client:
        result = await client.call_tool(
            "triage_issue",
            {"message": "The HR portal is down and nobody can log in."},
        )

    # FastMCP wraps the return value in content blocks
    assert not result.is_error
    text = result.data  # fastmcp exposes .data as the unwrapped string
    assert isinstance(text, str)
    assert len(text) > 20  # agent produced a real reply, not empty


@pytest.mark.asyncio
async def test_triage_issue_mentions_priority():
    # The agent instructions require it to always end with a priority.
    async with Client(mcp) as client:
        result = await client.call_tool(
            "triage_issue",
            {"message": "VPN is completely down for the entire engineering team."},
        )

    text = result.data.lower()
    assert "p1" in text or "p2" in text or "priority" in text or "critical" in text


@pytest.mark.asyncio
async def test_triage_issue_tool_has_helpful_description():
    # The docstring is what MCP Inspector shows users — verify it's meaningful.
    async with Client(mcp) as client:
        tools = await client.list_tools()
        triage_tool = next(t for t in tools if t.name == "triage_issue")

    assert triage_tool.description is not None
    assert len(triage_tool.description) > 20
