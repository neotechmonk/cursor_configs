"""Tests for _calculate_lookup_reference_value function in wrb.py."""

import pytest

from src.steps.technical.wrb import _calculate_lookup_reference_value


@pytest.mark.parametrize(
    "test_data",
    [
        pytest.param(
            {
                "ranges": [1.0, 2.0, 3.0],
                "method": "max",
                "expected": 3.0,
                "id": "max of multiple values"
            },
            id="max of multiple values"
        ),
        pytest.param(
            {
                "ranges": [1.0, 2.0, 3.0],
                "method": "avg",
                "expected": 2.0,
                "id": "avg of multiple values"
            },
            id="avg of multiple values"
        ),
        pytest.param(
            {
                "ranges": [1.0],
                "method": "max",
                "expected": 1.0,
                "id": "single value"
            },
            id="single value"
        ),
        pytest.param(
            {
                "ranges": [1.0, 1.0, 1.0],
                "method": "avg",
                "expected": 1.0,
                "id": "all same values"
            },
            id="all same values"
        ),
    ]
)
def test_calculate_lookup_reference_value_happy_path(test_data):
    """Test _calculate_lookup_reference_value with various valid scenarios."""
    result = _calculate_lookup_reference_value(
        ranges=test_data["ranges"],
        comparison_method=test_data["method"]
    )
    assert result == test_data["expected"]


def test_calculate_lookup_reference_value_invalid_method():
    """Test _calculate_lookup_reference_value with invalid comparison method."""
    with pytest.raises(ValueError, match="Invalid comparison method"):
        _calculate_lookup_reference_value([1.0, 2.0], "invalid")


def test_calculate_lookup_reference_value_zero_division():
    """Test _calculate_lookup_reference_value with zero values for average calculation."""
    with pytest.raises(ZeroDivisionError, match="Reference size is zero"):
        _calculate_lookup_reference_value([0.0, 0.0], "avg")


def test_calculate_lookup_reference_value_empty_input():
    """Test _calculate_lookup_reference_value with empty input."""
    with pytest.raises(ValueError, match="No ranges provided"):
        _calculate_lookup_reference_value([], "max") 