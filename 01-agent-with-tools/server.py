# server.py
# ──────────────────────────────────────────────────────────────
# FastMCP server — exposes the MAF agent as an MCP tool.
#
# The MCP client (MCP Inspector, a web app, another agent)
# only knows about one tool: triage_issue.
# It never sees the MAF agent or the tools inside.
# This clean boundary is the point of MCP.
#
# This file grows across the video series:
#   Video 1: one tool, progress streaming via MCP notifications
#   Video 2: adds AgentSession for multi-turn memory
#   Video 4: adds HITL pause/resume
# ──────────────────────────────────────────────────────────────

from fastmcp import Context, FastMCP
from agent_framework import FunctionInvocationContext, function_middleware

from agent import create_agent

# Create the FastMCP server
mcp = FastMCP("it-support-agent")

# Create the MAF agent once at module load
# (not per-request — Agent creation is expensive)
_agent = create_agent()

# Total number of tools the agent calls on every triage request.
# Used to drive the progress bar in MCP Inspector.
_TOOL_COUNT = 3


@mcp.tool()
async def triage_issue(message: str, ctx: Context) -> str:
    """
    Triage an IT support issue reported by an employee.

    Describe the problem and the affected system in plain language.
    The agent will check for open tickets, find the system owner,
    and recommend a priority level.

    Example: 'The HR portal is down and nobody can log in.'
    """
    # Track how many tools have been called so we can report
    # incremental progress to MCP Inspector as the agent works.
    step = 0

    @function_middleware
    async def progress_reporter(
        context: FunctionInvocationContext, call_next
    ) -> None:
        nonlocal step

        # Notify the MCP client that a tool call is starting.
        # MCP Inspector renders this as a live progress bar + label.
        await ctx.report_progress(
            progress=step,
            total=_TOOL_COUNT,
            message=f"Calling {context.function.name}...",
        )

        await call_next()  # execute the actual tool function

        step += 1

        # Notify again once the tool has returned so the bar advances.
        await ctx.report_progress(
            progress=step,
            total=_TOOL_COUNT,
            message=f"{context.function.name} complete",
        )

    # Pass the progress middleware as a per-request parameter so the
    # closure can capture `ctx` without rebuilding the agent each call.
    response = await _agent.run(message, middleware=[progress_reporter])

    # response.text is the agent's final synthesised triage summary
    return response.text


if __name__ == "__main__":
    # Run as SSE server so MCP Inspector can connect.
    # Connect MCP Inspector to: http://localhost:8000/sse
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
