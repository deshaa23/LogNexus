"""Structured diagnostics for LogNexus error events."""

import re
from dataclasses import dataclass

from src.log_parser import LogEntry
from src.root_cause import RootCauseResult


_CONNECTION_FAILURE_PATTERN = re.compile(
    r"connection\s+(?:refused|failure|failed)",
    re.IGNORECASE,
)


@dataclass
class DiagnosticEvent:
    """A structured description of one ERROR log event."""

    timestamp: str
    request_id: str | None
    service: str
    severity: str
    failure_pattern: str
    message: str


def build_diagnostics(
    entries: list[LogEntry],
    root_causes: list[RootCauseResult],
    failure_patterns: dict[str, int],
) -> list[DiagnosticEvent]:
    """Build chronological diagnostics for ERROR entries."""
    root_cause_by_request = {
        root_cause.request_id: root_cause for root_cause in root_causes
    }
    diagnostics: list[DiagnosticEvent] = []

    for entry in entries:
        if entry.level != "ERROR":
            continue

        failure_pattern = _classify_failure_pattern(entry.message)
        root_cause = root_cause_by_request.get(entry.request_id)
        severity = root_cause.severity if root_cause is not None else _severity_for_pattern(
            failure_pattern
        )
        diagnostics.append(
            DiagnosticEvent(
                timestamp=entry.timestamp,
                request_id=entry.request_id,
                service=entry.service,
                severity=severity,
                failure_pattern=failure_pattern,
                message=entry.message,
            )
        )

    return sorted(diagnostics, key=lambda diagnostic: diagnostic.timestamp)


def _classify_failure_pattern(message: str) -> str:
    """Classify an error message using the established failure rules."""
    normalized_message = message.lower()

    if _CONNECTION_FAILURE_PATTERN.search(normalized_message):
        return "CONNECTION_REFUSED"
    if "timeout" in normalized_message:
        return "TIMEOUT"
    if "unavailable" in normalized_message:
        return "SERVICE_UNAVAILABLE"
    return "GENERIC_FAILURE"


def _severity_for_pattern(failure_pattern: str) -> str:
    """Return the default severity for a failure pattern."""
    if failure_pattern == "CONNECTION_REFUSED":
        return "CRITICAL"
    if failure_pattern in {"TIMEOUT", "SERVICE_UNAVAILABLE", "GENERIC_FAILURE"}:
        return "HIGH" if failure_pattern != "GENERIC_FAILURE" else "MEDIUM"
    return "MEDIUM"
