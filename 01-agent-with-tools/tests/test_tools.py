# tests/test_tools.py
# ──────────────────────────────────────────────────────────────
# Unit tests for the three @tool functions.
# No API key required — all mock data, runs offline.
# ──────────────────────────────────────────────────────────────

import pytest

from tools import get_priority_recommendation, get_system_owner, get_ticket_status


# ── get_ticket_status ─────────────────────────────────────────

class TestGetTicketStatus:
    def test_known_system_returns_ticket(self):
        result = get_ticket_status("hr-portal")
        assert "INC-2847" in result
        assert "Open" in result

    def test_vpn_returns_in_progress_ticket(self):
        result = get_ticket_status("vpn")
        assert "INC-2831" in result
        assert "In Progress" in result

    def test_email_has_no_open_tickets(self):
        result = get_ticket_status("email")
        assert "No open tickets" in result

    def test_unknown_system_returns_not_found_message(self):
        result = get_ticket_status("payroll")
        assert "payroll" in result
        assert "No open tickets found" in result

    def test_lookup_is_case_insensitive(self):
        # The agent may pass system names in any case
        assert get_ticket_status("HR-PORTAL") == get_ticket_status("hr-portal")


# ── get_system_owner ──────────────────────────────────────────

class TestGetSystemOwner:
    def test_hr_portal_returns_hr_team(self):
        result = get_system_owner("hr-portal")
        assert "HR Systems Team" in result
        assert "hr-systems@company.com" in result

    def test_vpn_returns_network_team(self):
        result = get_system_owner("vpn")
        assert "Network Team" in result

    def test_email_returns_infra_team(self):
        result = get_system_owner("email")
        assert "Infrastructure Team" in result

    def test_unknown_system_returns_helpdesk_fallback(self):
        result = get_system_owner("unknown-app")
        assert "IT helpdesk" in result

    def test_lookup_is_case_insensitive(self):
        assert get_system_owner("VPN") == get_system_owner("vpn")


# ── get_priority_recommendation ───────────────────────────────

class TestGetPriorityRecommendation:
    def test_critical_system_plus_high_impact_is_p1(self):
        # Critical system + "down" trigger word → immediate escalation
        result = get_priority_recommendation("hr-portal", "System is down, nobody can log in")
        assert "P1" in result
        assert "Critical" in result

    def test_critical_system_low_impact_is_p2(self):
        # Critical system but vague impact → High priority, not P1
        result = get_priority_recommendation("vpn", "Some users are experiencing slowness")
        assert "P2" in result

    def test_non_critical_system_high_impact_is_p2(self):
        # Non-critical system but "all users blocked" → still P2
        result = get_priority_recommendation("wiki", "All users are blocked from editing")
        assert "P2" in result

    def test_non_critical_low_impact_is_p3(self):
        # Neither critical system nor impact keywords → standard queue
        result = get_priority_recommendation("wiki", "Page layout looks slightly off")
        assert "P3" in result

    def test_all_high_impact_trigger_words_detected(self):
        # Each trigger word in the list should produce P1 for a critical system
        trigger_words = ["down", "nobody", "all users", "blocked", "cannot", "entire"]
        for word in trigger_words:
            result = get_priority_recommendation("email", f"issue: {word} access")
            assert "P1" in result or "P2" in result, f"Expected P1/P2 for trigger word '{word}'"
