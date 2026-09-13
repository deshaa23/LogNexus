"""Tests for LogNexus failure pattern detection."""

from src.failure_patterns import detect_failure_patterns
from src.log_parser import LogEntry


def make_entry(level: str, message: str) -> LogEntry:
    """Create a test log entry with consistent fields."""
    return LogEntry(
        timestamp="2026-09-14 10:00:00",
        level=level,
        service="TestService",
        request_id="REQ001",
        message=message,
    )


def test_connection_failures_are_detected() -> None:
    entries = [make_entry("ERROR", "Connection refused by database")]

    assert detect_failure_patterns(entries) == {"CONNECTION_REFUSED": 1}


def test_timeouts_are_detected() -> None:
    entries = [make_entry("ERROR", "Request timeout")]

    assert detect_failure_patterns(entries) == {"TIMEOUT": 1}


def test_service_unavailable_is_detected() -> None:
    entries = [make_entry("ERROR", "Service unavailable")]

    assert detect_failure_patterns(entries) == {"SERVICE_UNAVAILABLE": 1}


def test_generic_failures_are_detected() -> None:
    entries = [make_entry("ERROR", "Operation failed")]

    assert detect_failure_patterns(entries) == {"GENERIC_FAILURE": 1}


def test_matching_is_case_insensitive() -> None:
    entries = [
        make_entry("ERROR", "CONNECTION REFUSED"),
        make_entry("ERROR", "Request TIMEOUT"),
        make_entry("ERROR", "SERVICE UNAVAILABLE"),
        make_entry("ERROR", "Operation FAILED"),
    ]

    assert detect_failure_patterns(entries) == {
        "CONNECTION_REFUSED": 1,
        "TIMEOUT": 1,
        "SERVICE_UNAVAILABLE": 1,
        "GENERIC_FAILURE": 1,
    }


def test_non_error_entries_are_ignored() -> None:
    entries = [
        make_entry("INFO", "Connection refused"),
        make_entry("WARNING", "Request timeout"),
    ]

    assert detect_failure_patterns(entries) == {}


def test_multiple_occurrences_are_counted() -> None:
    entries = [
        make_entry("ERROR", "Connection refused"),
        make_entry("ERROR", "Connection failure"),
        make_entry("ERROR", "Request timeout"),
        make_entry("ERROR", "Operation failed"),
        make_entry("ERROR", "Another operation failed"),
    ]

    assert detect_failure_patterns(entries) == {
        "CONNECTION_REFUSED": 2,
        "TIMEOUT": 1,
        "GENERIC_FAILURE": 2,
    }


def test_empty_input_returns_empty_dictionary() -> None:
    assert detect_failure_patterns([]) == {}
