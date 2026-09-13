"""Tests for LogNexus event correlation."""

from src.event_correlator import correlate_events
from src.log_parser import LogEntry


def make_entry(
    timestamp: str,
    request_id: str | None,
    message: str,
) -> LogEntry:
    """Create a test log entry with consistent default fields."""
    return LogEntry(
        timestamp=timestamp,
        level="INFO",
        service="TestService",
        request_id=request_id,
        message=message,
    )


def test_entries_with_same_request_id_are_grouped() -> None:
    first = make_entry("2026-09-14 10:00:01", "REQ001", "first")
    second = make_entry("2026-09-14 10:00:02", "REQ001", "second")

    result = correlate_events([first, second])

    assert result == {"REQ001": [first, second]}


def test_different_request_ids_create_separate_groups() -> None:
    first = make_entry("2026-09-14 10:00:01", "REQ001", "first")
    second = make_entry("2026-09-14 10:00:02", "REQ002", "second")

    result = correlate_events([first, second])

    assert result == {"REQ001": [first], "REQ002": [second]}


def test_events_are_returned_in_chronological_order() -> None:
    later = make_entry("2026-09-14 10:00:02", "REQ001", "later")
    earlier = make_entry("2026-09-14 10:00:01", "REQ001", "earlier")

    result = correlate_events([later, earlier])

    assert result["REQ001"] == [earlier, later]


def test_entries_without_request_id_are_excluded() -> None:
    untracked = make_entry("2026-09-14 10:00:01", None, "untracked")
    tracked = make_entry("2026-09-14 10:00:02", "REQ001", "tracked")

    result = correlate_events([untracked, tracked])

    assert result == {"REQ001": [tracked]}


def test_empty_input_returns_empty_result() -> None:
    assert correlate_events([]) == {}


def test_single_event_is_correlated() -> None:
    entry = make_entry("2026-09-14 10:00:01", "REQ001", "single")

    result = correlate_events([entry])

    assert result == {"REQ001": [entry]}
