"""Log quality validation utilities for LogNexus."""

from dataclasses import dataclass
from pathlib import Path

from src.log_parser import LOG_LINE_PATTERN


@dataclass
class LogQualityResult:
    """Summary of valid and malformed non-empty log lines."""

    total_lines: int
    valid_entries: int
    malformed_entries: int
    malformed_lines: list[str]


def validate_log_quality(path: str | Path) -> LogQualityResult:
    """Validate non-empty lines in a log file using the parser's pattern."""
    total_lines = 0
    valid_entries = 0
    malformed_lines: list[str] = []

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        total_lines += 1
        if LOG_LINE_PATTERN.fullmatch(line):
            valid_entries += 1
        else:
            malformed_lines.append(line)

    return LogQualityResult(
        total_lines=total_lines,
        valid_entries=valid_entries,
        malformed_entries=len(malformed_lines),
        malformed_lines=malformed_lines,
    )
