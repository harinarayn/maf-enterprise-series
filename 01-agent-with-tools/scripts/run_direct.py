# scripts/run_direct.py
# ──────────────────────────────────────────────────────────────
# Run the agent directly — no MCP server needed.
# Use this during development to test the agent quickly.
# On camera we use server.py + MCP Inspector instead.
#
# Run from the repo root:
#   python 01-agent-with-tools/scripts/run_direct.py
# ──────────────────────────────────────────────────────────────

import sys
from pathlib import Path

# Add the source directory to the path so imports work when
# this script is invoked from outside 01-agent-with-tools/.
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio

from agent import create_agent

TEST_MESSAGE = (
    "The HR portal is down and nobody can submit their timesheets. "
    "This is affecting the whole finance team."
)


async def main():
    agent = create_agent()

    print("Message:", TEST_MESSAGE)
    print("-" * 60)

    # Non-streaming response — MAF runs the full tool-calling loop
    # and returns one final synthesised reply.
    response = await agent.run(TEST_MESSAGE)
    print(response.text)


asyncio.run(main())
