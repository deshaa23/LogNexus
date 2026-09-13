"""Basic utilities for reading LogNexus input logs."""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LogEntry:
    """A parsed LogNexus log entry."""

    timestamp: str
    level: str
    service: str
    request_id: str | None
    message: str


LOG_LINE_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"(?P<level>\S+) (?P<service>\S+) "
    r"(?:RequestID=(?P<request_id>\S+) )?"
    r"(?P<message>.+)$"
)


def parse_log(path: str | Path) -> list[LogEntry]:
    """Parse valid log lines from *path* and skip malformed lines."""
    entries: list[LogEntry] = []

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        match = LOG_LINE_PATTERN.match(line)
        if match is None:
            continue

        entries.append(LogEntry(**match.groupdict()))

    return entries
