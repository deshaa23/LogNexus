"""Tests for the LogNexus log parser."""

from pathlib import Path

import pytest

from src.log_parser import LogEntry, parse_log

PROJECT_ROOT = Path(__file__).parents[1]


def test_parse_valid_info_entry(tmp_path: Path) -> None:
    log_file = tmp_path / "info.log"
    log_file.write_text(
        "2026-09-13 10:01:07 INFO ApiService RequestID=REQ001 Request received\n",
        encoding="utf-8",
    )

    entries = parse_log(log_file)

    assert entries == [
        LogEntry(
            timestamp="2026-09-13 10:01:07",
            level="INFO",
            service="ApiService",
            request_id="REQ001",
            message="Request received",
        )
    ]


@pytest.mark.parametrize("level", ["ERROR", "WARNING"])
def test_parse_error_and_warning_entries(tmp_path: Path, level: str) -> None:
    log_file = tmp_path / "levels.log"
    log_file.write_text(
        f"2026-09-13 10:01:07 {level} WorkerService RequestID=REQ002 Problem found\n",
        encoding="utf-8",
    )

    entry = parse_log(log_file)[0]

    assert entry.level == level


def test_skip_malformed_entries(tmp_path: Path) -> None:
    log_file = tmp_path / "malformed.log"
    log_file.write_text(
        "not a valid log line\n"
        "2026-09-13 10:01:07 INFO ApiService RequestID=REQ001 Valid entry\n"
        "2026-09-13 10:01:08 ERROR MissingRequestId Error entry\n",
        encoding="utf-8",
    )

    entries = parse_log(log_file)

    assert len(entries) == 2
    assert entries[0].request_id == "REQ001"
    assert entries[1].request_id is None


def test_parse_multiple_entries_from_sample_log() -> None:
    entries = parse_log(PROJECT_ROOT / "logs" / "sample.log")

    assert len(entries) == 3
    assert [entry.level for entry in entries] == ["INFO", "WARNING", "ERROR"]


def test_parser_returns_log_entry_objects() -> None:
    entries = parse_log(PROJECT_ROOT / "logs" / "sample.log")

    assert all(isinstance(entry, LogEntry) for entry in entries)
