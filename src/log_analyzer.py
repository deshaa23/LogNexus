"""Analysis utilities for parsed LogNexus log entries."""

from dataclasses import dataclass

from src.log_parser import LogEntry


@dataclass
class AnalysisResult:
    """Summary of log levels, warnings, errors, and affected services."""

    level_counts: dict[str, int]
    errors: list[LogEntry]
    warnings: list[LogEntry]
    error_services: set[str]


def analyze_logs(entries: list[LogEntry]) -> AnalysisResult:
    """Analyze log entries and return counts and error-related findings."""
    level_counts: dict[str, int] = {}
    errors: list[LogEntry] = []
    warnings: list[LogEntry] = []
    error_services: set[str] = set()

    for entry in entries:
        level_counts[entry.level] = level_counts.get(entry.level, 0) + 1

        if entry.level == "ERROR":
            errors.append(entry)
            error_services.add(entry.service)
        elif entry.level == "WARNING":
            warnings.append(entry)

    return AnalysisResult(
        level_counts=level_counts,
        errors=errors,
        warnings=warnings,
        error_services=error_services,
    )
