"""Run the complete LogNexus regression test suite."""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_regression() -> int:
    """Run pytest from the project root and return its exit code."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest"],
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode == 0:
        print("Regression suite PASSED")
    else:
        print(f"Regression suite FAILED (exit code {result.returncode})")

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(run_regression())
