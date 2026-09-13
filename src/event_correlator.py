"""Utilities for correlating LogNexus events by request ID."""

from src.log_parser import LogEntry


CorrelatedEvents = dict[str, list[LogEntry]]


def correlate_events(entries: list[LogEntry]) -> CorrelatedEvents:
    """Group log entries by request ID in chronological order.

    Entries without a request ID are excluded because they cannot be
    correlated reliably with another event.
    """
    grouped: CorrelatedEvents = {}

    for entry in entries:
        if entry.request_id is None:
            continue
        grouped.setdefault(entry.request_id, []).append(entry)

    for request_id, request_entries in grouped.items():
        grouped[request_id] = sorted(
            request_entries,
            key=lambda entry: entry.timestamp,
        )

    return grouped
