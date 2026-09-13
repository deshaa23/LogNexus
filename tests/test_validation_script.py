"""Tests for the Linux validation script."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "validate.sh"


def test_validation_script_has_required_bash_configuration() -> None:
    contents = SCRIPT_PATH.read_text(encoding="utf-8")

    assert contents.startswith("#!/usr/bin/env bash")
    assert "set -euo pipefail" in contents
    assert "python -m pytest" in contents
    assert "PASS:" in contents
    assert "FAIL:" in contents
    assert "exit \"$test_status\"" in contents


def _working_bash() -> str | None:
    """Return a usable Bash executable, if one is available."""
    bash = shutil.which("bash")
    if bash is None:
        return None

    try:
        result = subprocess.run(
            [bash, "-c", "exit 0"],
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    return bash if result.returncode == 0 else None


def test_validation_script_returns_pytest_failure_status(tmp_path: Path) -> None:
    bash = _working_bash()
    if bash is None:
        if sys.platform == "win32":
            pytest.skip("A usable Bash environment is not available on Windows")
        pytest.fail("Bash is required on Linux and macOS")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_python = fake_bin / "python"
    fake_python.write_text(
        "#!/usr/bin/env bash\n"
        "exit 17\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"

    result = subprocess.run(
        [bash, str(SCRIPT_PATH)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 17
    assert "FAIL:" in result.stdout
