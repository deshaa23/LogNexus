"""Tests for the LogNexus diagnostic report generator."""

from src.log_analyzer import AnalysisResult
from src.log_parser import LogEntry
from src.report_generator import generate_report
from src.root_cause import RootCauseResult


def make_entry(level: str, service: str) -> LogEntry:
    """Create a log entry for report test data."""
    return LogEntry(
        timestamp="2026-09-14 10:00:00",
        level=level,
        service=service,
        request_id="REQ001",
        message=f"{level} message",
    )


def test_report_contains_total_event_count() -> None:
    analysis = AnalysisResult(
        level_counts={"INFO": 2, "ERROR": 1},
        errors=[make_entry("ERROR", "DatabaseService")],
        warnings=[],
        error_services={"DatabaseService"},
    )

    report = generate_report(analysis, [])

    assert "Total log events: 3" in report


def test_report_contains_error_and_warning_counts() -> None:
    analysis = AnalysisResult(
        level_counts={"ERROR": 2, "WARNING": 3},
        errors=[make_entry("ERROR", "DatabaseService")] * 2,
        warnings=[make_entry("WARNING", "ApiService")] * 3,
        error_services={"DatabaseService"},
    )

    report = generate_report(analysis, [])

    assert "Error count: 2" in report
    assert "Warning count: 3" in report


def test_report_contains_affected_services() -> None:
    analysis = AnalysisResult(
        level_counts={"ERROR": 1},
        errors=[make_entry("ERROR", "DatabaseService")],
        warnings=[],
        error_services={"ApiService", "DatabaseService"},
    )

    report = generate_report(analysis, [])

    assert "Affected/error services: ApiService, DatabaseService" in report


def test_report_contains_root_cause_details() -> None:
    analysis = AnalysisResult({}, [], [], set())
    root_cause = RootCauseResult(
        request_id="REQ001",
        root_cause_service="DatabaseService",
        root_cause_message="Connection refused",
        severity="CRITICAL",
        affected_services=["ApiService"],
    )

    report = generate_report(analysis, [root_cause])

    assert "Request ID: REQ001" in report
    assert "Service: DatabaseService" in report
    assert "Message: Connection refused" in report
    assert "Severity: CRITICAL" in report
    assert "Affected services: ApiService" in report


def test_report_handles_no_root_causes() -> None:
    analysis = AnalysisResult({}, [], [], set())

    report = generate_report(analysis, [])

    assert "None detected" in report


def test_report_handles_empty_analysis() -> None:
    report = generate_report(AnalysisResult({}, [], [], set()), [])

    assert "Total log events: 0" in report
    assert "Error count: 0" in report
    assert "Warning count: 0" in report
    assert "Affected/error services: None" in report
