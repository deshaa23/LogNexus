"""Tests for LogNexus log quality validation."""

from pathlib import Path

from src.log_quality import LogQualityResult, validate_log_quality


def write_log(tmp_path: Path, content: str) -> Path:
    """Write test content to a temporary log file."""
    log_file = tmp_path / "quality.log"
    log_file.write_text(content, encoding="utf-8")
    return log_file


def test_all_valid_log_lines(tmp_path: Path) -> None:
    log_file = write_log(
        tmp_path,
        "2026-09-14 10:00:00 INFO ApiService RequestID=REQ001 Started\n"
        "2026-09-14 10:00:01 ERROR DatabaseService Connection failed\n",
    )

    result = validate_log_quality(log_file)

    assert result == LogQualityResult(2, 2, 0, [])


def test_malformed_log_lines_are_counted(tmp_path: Path) -> None:
    malformed_line = "not a valid log line"
    result = validate_log_quality(write_log(tmp_path, malformed_line + "\n"))

    assert result.total_lines == 1
    assert result.valid_entries == 0
    assert result.malformed_entries == 1


def test_mixed_valid_and_malformed_lines(tmp_path: Path) -> None:
    result = validate_log_quality(
        write_log(
            tmp_path,
            "2026-09-14 10:00:00 INFO ApiService Started\n"
            "malformed entry\n",
        )
    )

    assert result.total_lines == 2
    assert result.valid_entries == 1
    assert result.malformed_entries == 1


def test_blank_lines_are_ignored(tmp_path: Path) -> None:
    result = validate_log_quality(
        write_log(
            tmp_path,
            "\n  \n2026-09-14 10:00:00 INFO ApiService Started\n\n",
        )
    )

    assert result == LogQualityResult(1, 1, 0, [])


def test_empty_file_returns_empty_quality_result(tmp_path: Path) -> None:
    result = validate_log_quality(write_log(tmp_path, ""))

    assert result == LogQualityResult(0, 0, 0, [])


def test_malformed_lines_are_preserved(tmp_path: Path) -> None:
    malformed_lines = ["bad entry", "another malformed entry"]
    result = validate_log_quality(write_log(tmp_path, "\n".join(malformed_lines)))

    assert result.malformed_lines == malformed_lines


def test_quality_counts_are_correct(tmp_path: Path) -> None:
    result = validate_log_quality(
        write_log(
            tmp_path,
            "2026-09-14 10:00:00 INFO ApiService Started\n"
            "bad entry\n"
            "2026-09-14 10:00:02 WARNING ApiService RequestID=REQ001 Slow\n"
            "invalid entry\n",
        )
    )

    assert result.total_lines == 4
    assert result.valid_entries == 2
    assert result.malformed_entries == 2
