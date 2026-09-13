"""Command-line entry point for LogNexus diagnostics."""

import argparse
from pathlib import Path

from src.event_correlator import correlate_events
from src.failure_patterns import detect_failure_patterns
from src.log_analyzer import analyze_logs
from src.log_parser import parse_log
from src.report_generator import generate_report
from src.root_cause import detect_root_causes


def main(argv: list[str] | None = None) -> int:
    """Process a log file and print its diagnostic report."""
    parser = argparse.ArgumentParser(description="Analyze a LogNexus log file.")
    parser.add_argument("log_path", help="path to the log file to analyze")
    args = parser.parse_args(argv)

    log_path = Path(args.log_path)
    if not log_path.is_file():
        parser.error(f"log file does not exist: {log_path}")

    try:
        entries = parse_log(log_path)
    except OSError as error:
        parser.error(f"unable to read log file {log_path}: {error}")

    analysis = analyze_logs(entries)
    correlated_events = correlate_events(entries)
    root_causes = detect_root_causes(correlated_events)
    detect_failure_patterns(entries)

    print(generate_report(analysis, root_causes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
