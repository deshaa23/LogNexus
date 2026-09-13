"""Tests for LogNexus root cause detection."""

import pytest

from src.log_parser import LogEntry
from src.root_cause import RootCauseResult, detect_root_causes


def make_entry(
    timestamp: str,
    level: str,
    service: str,
    message: str,
    request_id: str = "REQ001",
) -> LogEntry:
    """Create a test log entry with a consistent request ID by default."""
    return LogEntry(
        timestamp=timestamp,
        level=level,
        service=service,
        request_id=request_id,
        message=message,
    )


def test_earliest_error_is_selected_with_correct_details() -> None:
    first_error = make_entry(
        "2026-09-14 10:00:01",
        "ERROR",
        "DatabaseService",
        "Connection timeout",
    )
    later_error = make_entry(
        "2026-09-14 10:00:02",
        "ERROR",
        "ApiService",
        "Request failed",
    )

    result = detect_root_causes({"REQ001": [later_error, first_error]})

    assert result[0].root_cause_service == "DatabaseService"
    assert result[0].root_cause_message == "Connection timeout"


@pytest.mark.parametrize(
    ("message", "severity"),
    [
        ("Connection timeout", "HIGH"),
        ("Connection refused", "CRITICAL"),
        ("Service unavailable", "HIGH"),
        ("Unexpected database error", "MEDIUM"),
    ],
)
def test_error_message_assigns_expected_severity(
    message: str,
    severity: str,
) -> None:
    entry = make_entry("2026-09-14 10:00:01", "ERROR", "DatabaseService", message)

    result = detect_root_causes({"REQ001": [entry]})

    assert result[0].severity == severity


def test_later_errors_from_other_services_are_affected_services() -> None:
    root_cause = make_entry(
        "2026-09-14 10:00:01",
        "ERROR",
        "DatabaseService",
        "Connection timeout",
    )
    affected_api = make_entry(
        "2026-09-14 10:00:02",
        "ERROR",
        "ApiService",
        "Request failed",
    )
    affected_worker = make_entry(
        "2026-09-14 10:00:03",
        "ERROR",
        "WorkerService",
        "Service unavailable",
    )

    result = detect_root_causes({"REQ001": [root_cause, affected_api, affected_worker]})

    assert result[0].affected_services == ["ApiService", "WorkerService"]
    assert "DatabaseService" not in result[0].affected_services


def test_request_without_errors_produces_no_root_cause() -> None:
    entries = [make_entry("2026-09-14 10:00:01", "INFO", "ApiService", "Started")]

    assert detect_root_causes({"REQ001": entries}) == []


def test_empty_correlated_events_produce_empty_result() -> None:
    assert detect_root_causes({}) == []
