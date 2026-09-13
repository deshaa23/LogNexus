"""Tests for LogNexus failure injection."""

import pytest

from src.event_correlator import correlate_events
from src.failure_injector import inject_failure
from src.failure_patterns import detect_failure_patterns


@pytest.mark.parametrize(
    ("scenario", "service"),
    [
        ("connection_refused", "DatabaseService"),
        ("timeout", "DatabaseService"),
        ("service_unavailable", "PaymentService"),
        ("generic_failure", "WorkerService"),
    ],
)
def test_each_scenario_creates_expected_error(
    scenario: str,
    service: str,
) -> None:
    entries = inject_failure(scenario)

    errors = [entry for entry in entries if entry.level == "ERROR"]

    assert len(errors) == 1
    assert errors[0].service == service


@pytest.mark.parametrize(
    ("scenario", "pattern"),
    [
        ("connection_refused", "CONNECTION_REFUSED"),
        ("timeout", "TIMEOUT"),
        ("service_unavailable", "SERVICE_UNAVAILABLE"),
        ("generic_failure", "GENERIC_FAILURE"),
    ],
)
def test_failure_scenario_is_detected(scenario: str, pattern: str) -> None:
    entries = inject_failure(scenario)

    assert detect_failure_patterns(entries) == {pattern: 1}


def test_generated_events_can_be_correlated_by_request_id() -> None:
    entries = inject_failure("timeout")

    correlated = correlate_events(entries)

    assert len(correlated) == 1
    request_id = entries[0].request_id
    assert request_id is not None
    assert correlated[request_id] == entries


def test_unsupported_scenario_raises_value_error() -> None:
    with pytest.raises(ValueError, match="unsupported failure scenario"):
        inject_failure("unknown")
