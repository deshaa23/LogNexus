"""Tests for the LogNexus log analyzer."""

from src.log_analyzer import analyze_logs
from src.log_parser import LogEntry


def test_count_log_levels() -> None:
    entries = [
        LogEntry("2026-09-14 10:00:00", "INFO", "ApiService", None, "Started"),
        LogEntry("2026-09-14 10:00:01", "WARNING", "ApiService", None, "Slow response"),
        LogEntry("2026-09-14 10:00:02", "ERROR", "DatabaseService", "REQ001", "Timeout"),
        LogEntry("2026-09-14 10:00:03", "ERROR", "ApiService", "REQ002", "Request failed"),
    ]

    result = analyze_logs(entries)

    assert result.level_counts == {"INFO": 1, "WARNING": 1, "ERROR": 2}


def test_collect_error_entries() -> None:
    error_entry = LogEntry(
        "2026-09-14 10:00:02", "ERROR", "DatabaseService", "REQ001", "Timeout"
    )
    entries = [
        LogEntry("2026-09-14 10:00:00", "INFO", "ApiService", None, "Started"),
        error_entry,
    ]

    result = analyze_logs(entries)

    assert result.errors == [error_entry]


def test_collect_warning_entries() -> None:
    warning_entry = LogEntry(
        "2026-09-14 10:00:01", "WARNING", "ApiService", None, "Slow response"
    )
    entries = [
        LogEntry("2026-09-14 10:00:00", "INFO", "ApiService", None, "Started"),
        warning_entry,
    ]

    result = analyze_logs(entries)

    assert result.warnings == [warning_entry]


def test_identify_services_that_generated_errors() -> None:
    entries = [
        LogEntry("2026-09-14 10:00:00", "ERROR", "DatabaseService", "REQ001", "Timeout"),
        LogEntry("2026-09-14 10:00:01", "ERROR", "ApiService", "REQ002", "Request failed"),
        LogEntry("2026-09-14 10:00:02", "ERROR", "DatabaseService", None, "Connection lost"),
    ]

    result = analyze_logs(entries)

    assert result.error_services == {"DatabaseService", "ApiService"}


def test_handle_empty_log_entries() -> None:
    result = analyze_logs([])

    assert result.level_counts == {}
    assert result.errors == []
    assert result.warnings == []
    assert result.error_services == set()


def test_handle_info_only_entries() -> None:
    entries = [
        LogEntry("2026-09-14 10:00:00", "INFO", "ApiService", None, "Started"),
        LogEntry("2026-09-14 10:00:01", "INFO", "WorkerService", None, "Ready"),
    ]

    result = analyze_logs(entries)

    assert result.level_counts == {"INFO": 2}
    assert result.errors == []
    assert result.warnings == []
    assert result.error_services == set()
