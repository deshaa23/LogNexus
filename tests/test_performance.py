"""Performance coverage for the LogNexus parsing and analysis pipeline."""

from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter

import pytest

from src.log_analyzer import analyze_logs
from src.log_parser import parse_log


ENTRY_COUNT = 10_000


@pytest.fixture
def large_log_file(tmp_path: Path) -> Path:
    """Create a deterministic log file with 10,000 valid entries."""
    start = datetime(2026, 9, 14, 10, 0, 0)
    levels = ("INFO", "WARNING", "ERROR")
    services = ("ApiService", "DatabaseService", "WorkerService")

    lines = [
        (
            f"{start + timedelta(seconds=index):%Y-%m-%d %H:%M:%S} "
            f"{levels[index % len(levels)]} "
            f"{services[index % len(services)]} "
            f"RequestID=REQ{index % 1000:04d} Event {index} processed"
        )
        for index in range(ENTRY_COUNT)
    ]

    log_file = tmp_path / "large.log"
    log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return log_file


def test_parse_log_processes_large_file(large_log_file: Path) -> None:
    entries = parse_log(large_log_file)

    assert len(entries) == ENTRY_COUNT
    assert entries[0].service == "ApiService"
    assert entries[-1].request_id == "REQ0999"


def test_analyze_logs_processes_large_input(large_log_file: Path) -> None:
    entries = parse_log(large_log_file)

    result = analyze_logs(entries)

    assert sum(result.level_counts.values()) == ENTRY_COUNT
    assert len(result.errors) == ENTRY_COUNT // 3
    assert len(result.warnings) == ENTRY_COUNT // 3


def test_parse_and_analysis_pipeline_completes_within_reasonable_limit(
    large_log_file: Path,
) -> None:
    start_time = perf_counter()

    entries = parse_log(large_log_file)
    result = analyze_logs(entries)

    elapsed_seconds = perf_counter() - start_time

    assert len(entries) == ENTRY_COUNT
    assert sum(result.level_counts.values()) == ENTRY_COUNT
    assert elapsed_seconds < 10
