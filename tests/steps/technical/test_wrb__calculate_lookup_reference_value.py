"""Tests for calculate_reference_range function in wrb.py."""

import pytest

from src.steps.technical.wrb import calculate_reference_range


@pytest.mark.parametrize(
    "test_data",
    [
        pytest.param(
            {
                "ranges": [8.0, 10.0, 12.0],
                "method": "max",
                "expected": 12.0,
                "description": "max of multiple values"
            },
            id="max of multiple values"
        ),
        pytest.param(
            {
                "ranges": [8.0, 10.0, 12.0],
                "method": "avg",
                "expected": 10.0,
                "description": "avg of multiple values"
            },
            id="avg of multiple values"
        ),
        pytest.param(
            {
                "ranges": [10.0],
                "method": "max",
                "expected": 10.0,
                "description": "single value"
            },
            id="single value"
        ),
        pytest.param(
            {
                "ranges": [10.0, 10.0, 10.0],
                "method": "avg",
                "expected": 10.0,
                "description": "all same values"
            },
            id="all same values"
        ),
    ]
)
def test_calculate_reference_range_happy_path(test_data):
    """Test calculate_reference_range with valid inputs."""
    result = calculate_reference_range(
        ranges=test_data["ranges"],
        comparison_method=test_data["method"]
    )
    assert result == test_data["expected"], f"Failed for {test_data['description']}: expected {test_data['expected']}, got {result}"


def test_calculate_reference_range_invalid_method():
    """Test calculate_reference_range with invalid comparison method."""
    with pytest.raises(ValueError, match="Invalid comparison method"):
        calculate_reference_range([8.0, 10.0], "invalid")


def test_calculate_reference_range_zero_division():
    """Test calculate_reference_range with zero values."""
    with pytest.raises(ZeroDivisionError, match="Reference size is zero"):
        calculate_reference_range([0.0, 0.0], "avg")


def test_calculate_reference_range_empty_input():
    """Test calculate_reference_range with empty input."""
    with pytest.raises(ValueError, match="No ranges provided"):
        calculate_reference_range([], "max") 