"""End-to-end tests for the LogNexus diagnostic pipeline."""

from pathlib import Path

from src.event_correlator import correlate_events
from src.failure_patterns import detect_failure_patterns
from src.log_analyzer import analyze_logs
from src.log_parser import parse_log
from src.report_generator import generate_report
from src.root_cause import detect_root_causes


def test_complete_diagnostic_pipeline(tmp_path: Path) -> None:
    log_file = tmp_path / "integration.log"
    log_file.write_text(
        "2026-09-14 10:00:00 INFO ApiService RequestID=REQ100 Request received\n"
        "2026-09-14 10:00:01 WARNING ApiService RequestID=REQ100 Request is slow\n"
        "2026-09-14 10:00:02 ERROR DatabaseService RequestID=REQ100 Connection refused\n"
        "2026-09-14 10:00:03 ERROR ApiService RequestID=REQ100 Request failed\n",
        encoding="utf-8",
    )

    entries = parse_log(log_file)
    analysis = analyze_logs(entries)
    correlated_events = correlate_events(entries)
    root_causes = detect_root_causes(correlated_events)
    failure_patterns = detect_failure_patterns(entries)
    report = generate_report(analysis, root_causes)

    assert len(entries) == 4
    assert analysis.level_counts == {"INFO": 1, "WARNING": 1, "ERROR": 2}
    assert len(analysis.errors) == 2
    assert len(analysis.warnings) == 1
    assert list(correlated_events) == ["REQ100"]
    assert correlated_events["REQ100"] == entries
    assert len(root_causes) == 1
    assert root_causes[0].root_cause_service == "DatabaseService"
    assert root_causes[0].severity == "CRITICAL"
    assert root_causes[0].affected_services == ["ApiService"]
    assert failure_patterns == {"CONNECTION_REFUSED": 1, "GENERIC_FAILURE": 1}
    assert "Total log events: 4" in report
    assert "Error count: 2" in report
    assert "Warning count: 1" in report
    assert "Request ID: REQ100" in report
    assert "Service: DatabaseService" in report
    assert "Severity: CRITICAL" in report
    assert "Affected services: ApiService" in report


def test_healthy_log_has_no_root_causes_or_failure_patterns(tmp_path: Path) -> None:
    log_file = tmp_path / "healthy.log"
    log_file.write_text(
        "2026-09-14 11:00:00 INFO ApiService RequestID=REQ200 Request received\n"
        "2026-09-14 11:00:01 WARNING ApiService RequestID=REQ200 Slow response\n",
        encoding="utf-8",
    )

    entries = parse_log(log_file)
    analysis = analyze_logs(entries)
    correlated_events = correlate_events(entries)
    root_causes = detect_root_causes(correlated_events)
    failure_patterns = detect_failure_patterns(entries)
    report = generate_report(analysis, root_causes)

    assert len(entries) == 2
    assert root_causes == []
    assert failure_patterns == {}
    assert "Total log events: 2" in report
    assert "Error count: 0" in report
    assert "Warning count: 1" in report
    assert "None detected" in report
