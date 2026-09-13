"""Tests for the LogNexus regression runner."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).parents[1]
RUNNER_PATH = PROJECT_ROOT / "scripts" / "run_regression.py"


def load_runner() -> ModuleType:
    """Load the regression runner module from its script path."""
    spec = importlib.util.spec_from_file_location("run_regression", RUNNER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_regression_runner_file_exists() -> None:
    assert RUNNER_PATH.is_file()


def test_runner_invokes_pytest_through_python(monkeypatch) -> None:
    runner = load_runner()
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    runner.run_regression()

    assert calls[0][0] == [sys.executable, "-m", "pytest"]
    assert calls[0][1]["cwd"] == runner.PROJECT_ROOT
    assert calls[0][1]["check"] is False


def test_runner_propagates_successful_exit_code(monkeypatch, capsys) -> None:
    runner = load_runner()
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0),
    )

    assert runner.run_regression() == 0
    assert "Regression suite PASSED" in capsys.readouterr().out


def test_runner_propagates_nonzero_failure_exit_code(monkeypatch, capsys) -> None:
    runner = load_runner()
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 7),
    )

    assert runner.run_regression() == 7
    assert "Regression suite FAILED" in capsys.readouterr().out


def test_runner_defines_clear_pass_fail_messages() -> None:
    contents = RUNNER_PATH.read_text(encoding="utf-8")

    assert "Regression suite PASSED" in contents
    assert "Regression suite FAILED" in contents
