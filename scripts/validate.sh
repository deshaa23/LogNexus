#!/usr/bin/env bash

set -euo pipefail

# Resolve the project root so validation works from any current directory.
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Run the complete test suite and preserve its exit status for CI/CD.
if python -m pytest; then
    echo "PASS: LogNexus test suite succeeded."
else
    test_status=$?
    echo "FAIL: LogNexus test suite failed (exit status ${test_status})."
    exit "$test_status"
fi
