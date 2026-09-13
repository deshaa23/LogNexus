# LogNexus

LogNexus is a Python system log analysis and diagnostic tool.

## Project structure

- `logs/`: sample and future input logs
- `src/`: application source code
- `tests/`: pytest-compatible tests
- `requirements.txt`: runtime dependencies

## Getting started

The initial parser uses only the Python standard library. From the project root:

```text
python -m pytest
```

Pytest is not included as a runtime dependency yet; install it in your development environment when adding the test workflow.
