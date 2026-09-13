"""Failure pattern detection for LogNexus error entries."""

import re

from src.log_parser import LogEntry


_CONNECTION_FAILURE_PATTERN = re.compile(r"connection\s+(?:refused|failure|failed)", re.IGNORECASE)


def detect_failure_patterns(entries: list[LogEntry]) -> dict[str, int]:
    """Count recognized failure patterns in ERROR log messages."""
    pattern_counts: dict[str, int] = {}

    for entry in entries:
        if entry.level != "ERROR":
            continue

        message = entry.message.lower()
        if _CONNECTION_FAILURE_PATTERN.search(message):
            pattern = "CONNECTION_REFUSED"
        elif "timeout" in message:
            pattern = "TIMEOUT"
        elif "unavailable" in message:
            pattern = "SERVICE_UNAVAILABLE"
        elif "failed" in message or "failure" in message:
            pattern = "GENERIC_FAILURE"
        else:
            continue

        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    return pattern_counts
