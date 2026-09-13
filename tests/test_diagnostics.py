"""Tests for structured LogNexus diagnostics."""

from src.diagnostics import DiagnosticEvent, build_diagnostics
from src.log_parser import LogEntry
from src.root_cause import RootCauseResult


def make_entry(
    timestamp: str,
    level: str,
    message: str,
    request_id: str | None = "REQ001",
    service: str = "DatabaseService",
) -> LogEntry:
    """Create a test log entry."""
    return LogEntry(timestamp, level, service, request_id, message)


def test_error_entries_produce_diagnostic_events() -> None:
    entry = make_entry("2026-09-14 10:00:00", "ERROR", "Connection refused")

    diagnostics = build_diagnostics([entry], [], {"CONNECTION_REFUSED": 1})

    assert diagnostics == [
        DiagnosticEvent(
            timestamp=entry.timestamp,
            request_id="REQ001",
            service="DatabaseService",
            severity="CRITICAL",
            failure_pattern="CONNECTION_REFUSED",
            message="Connection refused",
        )
    ]


def test_non_error_entries_are_ignored() -> None:
    entry = make_entry("2026-09-14 10:00:00", "WARNING", "Connection refused")

    assert build_diagnostics([entry], [], {}) == []


def test_connection_refused_errors_are_classified() -> None:
    entry = make_entry("2026-09-14 10:00:00", "ERROR", "Connection refused")

    diagnostic = build_diagnostics([entry], [], {"CONNECTION_REFUSED": 1})[0]

    assert diagnostic.failure_pattern == "CONNECTION_REFUSED"


def test_timeout_errors_are_classified() -> None:
    entry = make_entry("2026-09-14 10:00:00", "ERROR", "Database timeout")

    diagnostic = build_diagnostics([entry], [], {"TIMEOUT": 1})[0]

    assert diagnostic.failure_pattern == "TIMEOUT"


def test_root_cause_severity_is_included() -> None:
    entry = make_entry("2026-09-14 10:00:00", "ERROR", "Connection refused")
    root_cause = RootCauseResult("REQ001", "DatabaseService", entry.message, "CRITICAL", [])

    diagnostic = build_diagnostics([entry], [root_cause], {"CONNECTION_REFUSED": 1})[0]

    assert diagnostic.severity == "CRITICAL"


def test_request_id_is_preserved() -> None:
    entry = make_entry("2026-09-14 10:00:00", "ERROR", "Request failed", request_id="REQ007")

    diagnostic = build_diagnostics([entry], [], {"GENERIC_FAILURE": 1})[0]

    assert diagnostic.request_id == "REQ007"


def test_diagnostics_are_sorted_chronologically() -> None:
    later = make_entry("2026-09-14 10:00:02", "ERROR", "Request failed")
    earlier = make_entry("2026-09-14 10:00:01", "ERROR", "Database timeout")

    diagnostics = build_diagnostics(
        [later, earlier],
        [],
        {"GENERIC_FAILURE": 1, "TIMEOUT": 1},
    )

    assert [diagnostic.timestamp for diagnostic in diagnostics] == [
        "2026-09-14 10:00:01",
        "2026-09-14 10:00:02",
    ]


def test_empty_input_returns_empty_list() -> None:
    assert build_diagnostics([], [], {}) == []
