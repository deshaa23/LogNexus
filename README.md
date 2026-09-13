# LogNexus

Automated log analysis and failure diagnosis tooling for QA automation workflows.

## Overview

LogNexus turns application log files into structured diagnostic information. It parses log entries, identifies errors and warnings, correlates events by `RequestID`, detects likely root causes and failure patterns, and produces a readable report for investigating application failures.

The project also includes deterministic failure injection, log-quality validation, end-to-end coverage, performance checks, and regression runners to support repeatable QA validation.

## Key Features

- Log parsing with support for optional `RequestID` values
- Error and warning detection
- Event correlation using `RequestID`
- Rule-based root-cause detection
- Case-insensitive failure-pattern detection
- Structured failure diagnostics
- Human-readable diagnostic report generation
- Command-line interface for processing log files
- Deterministic failure injection for common scenarios
- Log-quality validation with malformed-line preservation
- End-to-end integration testing
- Large-log performance testing
- Python regression runner and Bash validation script

## Architecture

```text
Log File
		|
		v
	Parser
		+--> Analyzer --------------------------------+
		|                                             |
		+--> Event Correlator --> Root Cause Detection +--> Report Generator --> CLI
		|
		+--> Failure Pattern Detection

	ERROR entries + Root Causes + Failure Patterns --> Structured Diagnostics
```

The automated testing and validation layer exercises individual modules, the complete pipeline, large inputs, failure scenarios, and regression execution through pytest, Bash, and Python tooling. Structured diagnostics are available as a separate analysis utility; the current CLI report uses the analyzer and root-cause results.

## Project Structure

```text
LogNexus/
├── .github/
│   └── workflows/
│       └── ci.yml
├── logs/
│   └── sample.log
├── scripts/
│   ├── run_regression.py
│   └── validate.sh
├── src/
│   ├── diagnostics.py
│   ├── event_correlator.py
│   ├── failure_injector.py
│   ├── failure_patterns.py
│   ├── log_analyzer.py
│   ├── log_parser.py
│   ├── log_quality.py
│   ├── main.py
│   ├── report_generator.py
│   └── root_cause.py
├── tests/
│   ├── test_diagnostics.py
│   ├── test_event_correlator.py
│   ├── test_failure_injector.py
│   ├── test_failure_patterns.py
│   ├── test_integration.py
│   ├── test_log_analyzer.py
│   ├── test_log_parser.py
│   ├── test_log_quality.py
│   ├── test_main.py
│   ├── test_performance.py
│   ├── test_regression_runner.py
│   ├── test_report_generator.py
│   ├── test_root_cause.py
│   └── test_validation_script.py
├── requirements.txt
└── README.md
```

## Technology Stack

- Python 3.14 in GitHub Actions
- Python standard library modules including `argparse`, `dataclasses`, `pathlib`, `re`, `subprocess`, and `time`
- pytest for automated testing
- Bash for Linux-oriented validation
- GitHub Actions for CI

## Testing

The project uses pytest for focused unit tests covering parsing, analysis, correlation, root-cause rules, failure patterns, diagnostics, reporting, log quality, failure injection, and CLI behavior.

It also includes end-to-end pipeline tests, deterministic performance tests that generate 10,000 log entries, and regression-runner tests. The suite is intentionally discoverable through the standard command:

```bash
python -m pytest
```

## CI/CD

`.github/workflows/ci.yml` runs on pushes and pull requests targeting `main`. It uses `ubuntu-latest`, sets up Python 3.14, installs `requirements.txt` and pytest, and runs the complete suite with:

```bash
python -m pytest --junitxml=test-results.xml
```

The workflow uploads `test-results.xml` as the `lognexus-test-results` artifact with the official `actions/upload-artifact@v4` action, including when tests fail.

## Installation

```bash
git clone https://github.com/deshaa23/LogNexus.git
cd LogNexus
python -m venv .venv
```

Activate the virtual environment:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies and run the tests:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

## Usage

Process a log file with the CLI:

```bash
python -m src.main logs/sample.log
```

The CLI handles missing paths through argparse errors and produces a zero-event report for empty or malformed-only input.

## Example

For log entries containing an INFO event followed by a database connection failure, the report includes output like:

```text
LogNexus Diagnostic Report
===========================
Total log events: 3
Error count: 1
Warning count: 1
Affected/error services: DatabaseService

Root Causes
-----------
Request ID: REQ003
Service: DatabaseService
Message: Connection timeout
Severity: HIGH
Affected services: None
```

## QA Engineering Focus

LogNexus demonstrates:

- Automated unit testing with pytest
- Deterministic failure injection for connection, timeout, unavailable, and generic failure scenarios
- End-to-end integration testing across the diagnostic pipeline
- Regression testing through `scripts/run_regression.py`
- Log analysis and debugging through parsing, correlation, root-cause, and diagnostic modules
- CI/CD validation with GitHub Actions and JUnit test artifacts
- Linux/Bash validation through `scripts/validate.sh`
