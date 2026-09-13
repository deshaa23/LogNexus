"""Generate human-readable diagnostic reports for LogNexus."""

from src.log_analyzer import AnalysisResult
from src.root_cause import RootCauseResult


def generate_report(
    analysis: AnalysisResult,
    root_causes: list[RootCauseResult],
) -> str:
    """Return a deterministic diagnostic report from analysis results."""
    total_events = sum(analysis.level_counts.values())
    error_services = ", ".join(sorted(analysis.error_services)) or "None"
    lines = [
        "LogNexus Diagnostic Report",
        "===========================",
        f"Total log events: {total_events}",
        f"Error count: {len(analysis.errors)}",
        f"Warning count: {len(analysis.warnings)}",
        f"Affected/error services: {error_services}",
        "",
        "Root Causes",
        "-----------",
    ]

    if not root_causes:
        lines.append("None detected")
    else:
        for root_cause in root_causes:
            affected_services = ", ".join(root_cause.affected_services) or "None"
            lines.extend(
                [
                    f"Request ID: {root_cause.request_id}",
                    f"Service: {root_cause.root_cause_service}",
                    f"Message: {root_cause.root_cause_message}",
                    f"Severity: {root_cause.severity}",
                    f"Affected services: {affected_services}",
                    "",
                ]
            )

    return "\n".join(lines).rstrip()
