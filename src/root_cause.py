"""Rule-based root cause detection for correlated LogNexus events."""

import re
from dataclasses import dataclass

from src.event_correlator import CorrelatedEvents
from src.log_parser import LogEntry


@dataclass
class RootCauseResult:
    """The primary root cause and affected services for one request."""

    request_id: str
    root_cause_service: str
    root_cause_message: str
    severity: str
    affected_services: list[str]


def detect_root_causes(correlated_events: CorrelatedEvents) -> list[RootCauseResult]:
    """Detect the earliest error and affected services for each request ID."""
    results: list[RootCauseResult] = []

    for request_id, events in correlated_events.items():
        error_events = [entry for entry in events if entry.level == "ERROR"]
        if not error_events:
            continue

        root_cause = min(error_events, key=lambda entry: entry.timestamp)
        affected_services = _find_affected_services(events, root_cause)
        results.append(
            RootCauseResult(
                request_id=request_id,
                root_cause_service=root_cause.service,
                root_cause_message=root_cause.message,
                severity=_severity_for_message(root_cause.message),
                affected_services=affected_services,
            )
        )

    return results


def _severity_for_message(message: str) -> str:
    """Return the severity assigned to an error message."""
    normalized_message = message.lower()

    if re.search(r"connection.*(?:failure|failed|refused)|connection refused", normalized_message):
        return "CRITICAL"
    if "timeout" in normalized_message:
        return "HIGH"
    if re.search(r"unavailable|failed|failure", normalized_message):
        return "HIGH"
    return "MEDIUM"


def _find_affected_services(
    events: list[LogEntry],
    root_cause: LogEntry,
) -> list[str]:
    """Return unique services with errors after the root-cause event."""
    affected_services: list[str] = []
    root_cause_seen = False

    for event in events:
        if event is root_cause:
            root_cause_seen = True
            continue
        if root_cause_seen and event.level == "ERROR" and event.service not in affected_services:
            affected_services.append(event.service)

    return affected_services
