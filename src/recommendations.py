"""Rule-based troubleshooting recommendations for LogNexus failures."""

from dataclasses import dataclass


@dataclass
class Recommendation:
    """A troubleshooting recommendation for a detected failure pattern."""

    failure_pattern: str
    severity: str
    action: str


_RECOMMENDATIONS = {
    "CONNECTION_REFUSED": (
        "Check whether the target service is running, verify host and port "
        "configuration, and check network connectivity."
    ),
    "TIMEOUT": (
        "Check service response time, network connectivity, timeout "
        "configuration, and downstream service availability."
    ),
    "SERVICE_UNAVAILABLE": (
        "Check service health and status, dependencies, connectivity, and "
        "recent service failures."
    ),
    "GENERIC_FAILURE": (
        "Review the complete request flow and relevant application and "
        "service logs to identify the underlying failure."
    ),
}


def get_recommendation(failure_pattern: str, severity: str) -> Recommendation:
    """Return practical troubleshooting guidance for a failure pattern."""
    normalized_pattern = failure_pattern.upper()
    try:
        action = _RECOMMENDATIONS[normalized_pattern]
    except KeyError as error:
        raise ValueError(f"unsupported failure pattern: {failure_pattern}") from error

    return Recommendation(
        failure_pattern=normalized_pattern,
        severity=severity,
        action=action,
    )
