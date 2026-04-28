# agent.py
# ──────────────────────────────────────────────────────────────
# MAF Agent definition.
#
# An Agent in MAF has three things:
#   1. client       — the LLM provider (OpenAI here, swappable)
#   2. instructions — the system prompt defining agent behaviour
#   3. tools        — Python functions the agent can call
#
# The agent handles the tool-calling loop automatically.
# We do not write any orchestration logic here.
# ──────────────────────────────────────────────────────────────

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from config import settings
from tools import get_priority_recommendation, get_system_owner, get_ticket_status


def create_agent() -> Agent:
    """Create and return the IT support triage agent. Called once at server startup."""

    # The client is the LLM provider.
    # Swap OpenAIChatClient for AzureOpenAIChatClient or
    # AnthropicChatClient and nothing else in this file changes.
    client = OpenAIChatClient(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
    )

    # Instructions define what this agent is and how it behaves.
    # Keep these focused — one clear role, one clear outcome.
    instructions = (
        "You are an IT support triage assistant for a large enterprise. "
        "When an employee reports a system issue, you must: "
        "1. Check for an existing open ticket using get_ticket_status. "
        "2. Identify the system owner using get_system_owner. "
        "3. Recommend a priority level using get_priority_recommendation. "
        "Always summarise your findings clearly and concisely. "
        "End every response with the recommended next action for the employee."
    )

    return Agent(
        client=client,
        instructions=instructions,
        # All three tools registered here.
        # MAF decides which tools to call based on the message and docstrings.
        tools=[get_ticket_status, get_system_owner, get_priority_recommendation],
    )
