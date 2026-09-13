"""Tests for LogNexus troubleshooting recommendations."""

import pytest

from src.recommendations import Recommendation, get_recommendation


@pytest.mark.parametrize(
    ("failure_pattern", "expected_text"),
    [
        ("CONNECTION_REFUSED", "service is running"),
        ("TIMEOUT", "response time"),
        ("SERVICE_UNAVAILABLE", "service health"),
        ("GENERIC_FAILURE", "request flow"),
    ],
)
def test_recommendation_for_failure_pattern(
    failure_pattern: str,
    expected_text: str,
) -> None:
    recommendation = get_recommendation(failure_pattern, "HIGH")

    assert isinstance(recommendation, Recommendation)
    assert recommendation.failure_pattern == failure_pattern
    assert expected_text in recommendation.action.lower()


def test_pattern_matching_is_case_insensitive() -> None:
    recommendation = get_recommendation("timeout", "HIGH")

    assert recommendation.failure_pattern == "TIMEOUT"


def test_severity_is_preserved() -> None:
    recommendation = get_recommendation("GENERIC_FAILURE", "CRITICAL")

    assert recommendation.severity == "CRITICAL"


def test_unsupported_pattern_raises_value_error() -> None:
    with pytest.raises(ValueError, match="unsupported failure pattern"):
        get_recommendation("UNKNOWN_PATTERN", "MEDIUM")


def test_recommendation_contains_useful_action() -> None:
    recommendation = get_recommendation("CONNECTION_REFUSED", "CRITICAL")

    assert recommendation.action
    assert len(recommendation.action.split()) >= 5
