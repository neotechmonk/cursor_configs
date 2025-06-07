"""Tests for bar high-low range calculation functionality."""

import pandas as pd
import pytest

from src.models.base import PriceLabel
from src.steps.technical.wrb import _get_high_low_range_abs


@pytest.mark.parametrize(
    "test_data",
    [
        pytest.param(
            {
                "open": 100,
                "high": 110,
                "low": 95,
                "close": 105,
                "expected": 15,
                "description": "uptrend"
            },
            id="upbar"
        ),
        pytest.param(
            {
                "open": 110,
                "high": 115,
                "low": 90,
                "close": 95,
                "expected": 25,
                "description": "downtrend"
            },
            id="downbar"
        ),
        pytest.param(
            {
                "open": 100,
                "high": 105,
                "low": 95,
                "close": 100,
                "expected": 10,
                "description": "range/sideways"
            },
            id="same open and close"
        ),
    ]
)
def test_get_high_low_range_abs_happy_path(test_data):
    """Test _get_high_low_range_abs for up, down, and range trends."""
    index = pd.Timestamp("2024-01-01")
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [test_data["open"]],
        PriceLabel.HIGH: [test_data["high"]],
        PriceLabel.LOW: [test_data["low"]],
        PriceLabel.CLOSE: [test_data["close"]],
    }, index=[index])

    result = _get_high_low_range_abs(price_data, current_bar_index=index)
    assert result == test_data["expected"], f"Failed for {test_data['description']}: expected {test_data['expected']}, got {result}"


def test_get_high_low_range_abs_success():
    """Test successful calculation of bar high-low range."""
    index = pd.Timestamp("2024-01-01")
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100],
        PriceLabel.HIGH: [110],
        PriceLabel.LOW: [90],
        PriceLabel.CLOSE: [105],
    }, index=[index])
    
    bar_size = _get_high_low_range_abs(price_data, current_bar_index=index)
    expected_size = price_data.loc[index][PriceLabel.HIGH] - price_data.loc[index][PriceLabel.LOW]
    assert bar_size == expected_size


def test_get_high_low_range_abs_invalid_index():
    """Test bar high-low range calculation with invalid index."""
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100],
        PriceLabel.HIGH: [110],
        PriceLabel.LOW: [90],
        PriceLabel.CLOSE: [105],
    }, index=[pd.Timestamp("2024-01-01")])
    
    invalid_index = pd.Timestamp("2099-01-01")
    with pytest.raises(IndexError, match="Current bar index 2099-01-01 00:00:00 not found in data"):
        _get_high_low_range_abs(price_data, current_bar_index=invalid_index)


def test_get_high_low_range_abs_missing_columns():
    """Test bar high-low range calculation with missing price columns."""
    invalid_data = pd.DataFrame({'invalid': [1, 2, 3]})
    index = invalid_data.index[0]
    with pytest.raises(KeyError):
        _get_high_low_range_abs(invalid_data, current_bar_index=index)


def test_get_high_low_range_abs_correct_index():
    """Test that _get_high_low_range_abs fetches the correct index from the DataFrame."""
    indices = pd.date_range(start='2024-01-01', periods=3)
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 101, 102],
        PriceLabel.HIGH: [110, 111, 112],
        PriceLabel.LOW: [95, 96, 97],
        PriceLabel.CLOSE: [105, 106, 107],
    }, index=indices)

    # Test fetching the first index
    result = _get_high_low_range_abs(price_data, current_bar_index=indices[0])
    expected = 15  # high - low = 110 - 95 = 15
    assert result == expected, f"Failed to fetch correct index: expected {expected}, got {result}"

    # Test fetching the second index
    result = _get_high_low_range_abs(price_data, current_bar_index=indices[1])
    expected = 15  # high - low = 111 - 96 = 15
    assert result == expected, f"Failed to fetch correct index: expected {expected}, got {result}"

    # Test fetching the third index
    result = _get_high_low_range_abs(price_data, current_bar_index=indices[2])
    expected = 15  # high - low = 112 - 97 = 15
    assert result == expected, f"Failed to fetch correct index: expected {expected}, got {result}" 