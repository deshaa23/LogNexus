"""Deterministic failure injection utilities for LogNexus testing."""

from src.log_parser import LogEntry


_FAILURE_SCENARIOS: dict[str, tuple[str, str]] = {
    "connection_refused": ("DatabaseService", "Connection refused by database"),
    "timeout": ("DatabaseService", "Database request timeout"),
    "service_unavailable": ("PaymentService", "Payment service unavailable"),
    "generic_failure": ("WorkerService", "Background operation failed"),
}

_REQUEST_ID = "INJECTED-REQ-001"


def inject_failure(scenario: str) -> list[LogEntry]:
    """Generate a deterministic API-to-service flow for a failure scenario."""
    try:
        service, message = _FAILURE_SCENARIOS[scenario]
    except KeyError as error:
        raise ValueError(f"unsupported failure scenario: {scenario}") from error

    return [
        LogEntry(
            timestamp="2026-09-14 12:00:00",
            level="INFO",
            service="ApiService",
            request_id=_REQUEST_ID,
            message="Request received",
        ),
        LogEntry(
            timestamp="2026-09-14 12:00:01",
            level="ERROR",
            service=service,
            request_id=_REQUEST_ID,
            message=message,
        ),
    ]
