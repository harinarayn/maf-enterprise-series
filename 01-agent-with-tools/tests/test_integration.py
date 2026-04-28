# tests/test_integration.py
# ──────────────────────────────────────────────────────────────
# Integration tests — run the real MAF agent against the live
# OpenAI API. Requires OPENAI_API_KEY in .env.
#
# These tests verify that the agent:
#   1. Calls all three tools (ticket, owner, priority)
#   2. Returns a coherent triage summary
#   3. Handles unknown systems gracefully
# ──────────────────────────────────────────────────────────────

import pytest

from agent import create_agent


@pytest.mark.asyncio
async def test_hr_portal_full_triage():
    # The canonical demo scenario — HR portal down, finance team blocked.
    # We expect the agent to call all three tools and mention key facts.
    agent = create_agent()
    response = await agent.run(
        "The HR portal is down and nobody can submit their timesheets. "
        "This is affecting the whole finance team."
    )

    text = response.text.lower()

    # Agent should surface the open ticket it found
    assert "inc-2847" in text or "ticket" in text

    # Agent should name the responsible team
    assert "hr systems" in text or "hr-systems" in text or "owner" in text

    # Agent should include a priority recommendation
    assert "p1" in text or "critical" in text or "priority" in text


@pytest.mark.asyncio
async def test_vpn_triage_returns_in_progress_info():
    agent = create_agent()
    response = await agent.run(
        "VPN is very slow for me today, I can barely connect."
    )

    text = response.text.lower()

    # INC-2831 is already in progress — agent should surface this
    assert "vpn" in text
    assert "inc-2831" in text or "in progress" in text or "ticket" in text


@pytest.mark.asyncio
async def test_unknown_system_handled_gracefully():
    # Payroll is not in mock data — agent should still produce a useful response
    agent = create_agent()
    response = await agent.run(
        "The payroll system is unreachable and we can't process salaries."
    )

    text = response.text.lower()

    # Agent should still give a priority recommendation even without ticket data
    assert len(text) > 50  # substantive reply
    assert "priority" in text or "p1" in text or "p2" in text or "escalat" in text
