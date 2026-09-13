"""Generate human-readable diagnostic reports for LogNexus."""

from src.failure_patterns import detect_failure_patterns
from src.log_analyzer import AnalysisResult
from src.log_parser import LogEntry
from src.recommendations import get_recommendation
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
            failure_pattern = _get_failure_pattern(root_cause)
            lines.extend(
                [
                    f"Request ID: {root_cause.request_id}",
                    f"Root Cause: {root_cause.root_cause_message}",
                    f"Service: {root_cause.root_cause_service}",
                    f"Message: {root_cause.root_cause_message}",
                    f"Severity: {root_cause.severity}",
                    f"Failure Pattern: {failure_pattern or 'Unknown'}",
                    f"Affected services: {affected_services}",
                    "",
                    "Recommended Actions:",
                ]
            )
            if failure_pattern is None:
                lines.append("- No rule-based recommendation available.")
            else:
                recommendation = get_recommendation(
                    failure_pattern,
                    root_cause.severity,
                )
                lines.append(f"- {recommendation.action}")
            lines.append("")

    return "\n".join(lines).rstrip()


def _get_failure_pattern(root_cause: RootCauseResult) -> str | None:
    """Return the established failure pattern for a root-cause message."""
    entry = LogEntry(
        timestamp="",
        level="ERROR",
        service=root_cause.root_cause_service,
        request_id=root_cause.request_id,
        message=root_cause.root_cause_message,
    )
    patterns = detect_failure_patterns([entry])
    return next(iter(patterns), None)
