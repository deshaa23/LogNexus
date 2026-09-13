"""Tests for the LogNexus command-line interface."""

from pathlib import Path

from src.main import main


def test_cli_processes_valid_log_file(tmp_path: Path, capsys) -> None:
    log_file = tmp_path / "valid.log"
    log_file.write_text(
        "2026-09-14 10:00:00 INFO ApiService RequestID=REQ001 Started\n"
        "2026-09-14 10:00:01 ERROR DatabaseService RequestID=REQ001 Connection timeout\n",
        encoding="utf-8",
    )

    exit_code = main([str(log_file)])

    assert exit_code == 0
    assert "Total log events: 2" in capsys.readouterr().out


def test_cli_output_contains_diagnostic_report(tmp_path: Path, capsys) -> None:
    log_file = tmp_path / "report.log"
    log_file.write_text(
        "2026-09-14 10:00:00 ERROR DatabaseService RequestID=REQ001 Connection refused\n",
        encoding="utf-8",
    )

    main([str(log_file)])
    output = capsys.readouterr().out

    assert "LogNexus Diagnostic Report" in output
    assert "Request ID: REQ001" in output
    assert "Severity: CRITICAL" in output


def test_missing_file_produces_useful_error(tmp_path: Path, capsys) -> None:
    missing_file = tmp_path / "missing.log"

    try:
        main([str(missing_file)])
    except SystemExit as error:
        assert error.code == 2

    assert "log file does not exist" in capsys.readouterr().err


def test_empty_log_file_is_handled_gracefully(tmp_path: Path, capsys) -> None:
    log_file = tmp_path / "empty.log"
    log_file.write_text("", encoding="utf-8")

    exit_code = main([str(log_file)])

    assert exit_code == 0
    assert "Total log events: 0" in capsys.readouterr().out


def test_cli_returns_nonzero_exit_code_for_missing_path() -> None:
    try:
        main([])
    except SystemExit as error:
        assert error.code == 2
    else:
        raise AssertionError("main() should reject a missing log path")
