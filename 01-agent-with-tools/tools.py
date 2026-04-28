# tools.py
# ──────────────────────────────────────────────────────────────
# MAF Tools — plain Python functions the agent can call.
#
# Key rules:
#   - @tool decorator registers the function with MAF
#   - The docstring tells the agent WHEN and WHY to use this tool
#   - Field(description=...) tells the agent what each parameter means
#   - Return a plain string — the agent reads this as context
#
# In production: replace the mock data with real API calls,
# e.g. ServiceNow, CMDB, or your internal service catalogue.
# ──────────────────────────────────────────────────────────────

from typing import Annotated

from agent_framework import tool
from pydantic import Field


@tool
def get_ticket_status(
    system_name: Annotated[
        str,
        Field(description="Name of the IT system or application to check"),
    ]
) -> str:
    """
    Check if there is an open support ticket for this system.
    Use this first whenever an employee reports a system issue.
    """
    # Production: call ServiceNow or Jira API here
    # e.g. servicenow_client.get_open_incidents(system_name)
    tickets = {
        "hr-portal": "INC-2847 — Open — HR Portal login failures since 09:00",
        "email":     "No open tickets",
        "vpn":       "INC-2831 — In Progress — VPN latency under investigation",
    }
    return tickets.get(
        system_name.lower(),
        f"No open tickets found for '{system_name}'.",
    )


@tool
def get_system_owner(
    system_name: Annotated[
        str,
        Field(description="Name of the IT system or application"),
    ]
) -> str:
    """
    Look up the team responsible for a system and their contact details.
    Use this to tell the employee who to escalate to.
    """
    # Production: query your CMDB or service catalogue here
    # e.g. cmdb_client.get_owner(system_name)
    owners = {
        "hr-portal": "HR Systems Team — hr-systems@company.com",
        "email":     "Infrastructure Team — infra@company.com",
        "vpn":       "Network Team — network@company.com",
    }
    return owners.get(
        system_name.lower(),
        f"Owner not found for '{system_name}'. Contact the IT helpdesk.",
    )


@tool
def get_priority_recommendation(
    system_name: Annotated[
        str,
        Field(description="Name of the affected IT system"),
    ],
    business_impact: Annotated[
        str,
        Field(description="Description of the business impact from the employee"),
    ],
) -> str:
    """
    Recommend a support ticket priority based on system criticality
    and the reported business impact. Always use this before closing
    your response so the employee knows how urgently this will be handled.
    """
    # Production: query system criticality tier from CMDB
    # and apply your organisation's priority matrix here.
    critical_systems = ["hr-portal", "email", "payroll", "vpn", "erp"]
    high_impact_words = ["down", "nobody", "all users", "blocked", "cannot", "entire"]

    is_critical = system_name.lower() in critical_systems
    is_high_impact = any(w in business_impact.lower() for w in high_impact_words)

    if is_critical and is_high_impact:
        return "P1 — Critical. Escalate immediately to the system owner."
    elif is_critical or is_high_impact:
        return "P2 — High. Notify system owner within 30 minutes."
    else:
        return "P3 — Medium. Log and assign to the standard support queue."
