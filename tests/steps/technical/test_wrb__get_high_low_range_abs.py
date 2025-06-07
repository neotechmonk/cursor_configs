"""Tests for bar high-low range calculation functionality."""

import pandas as pd
import pytest

from src.models.base import PriceLabel
from src.steps.technical.wrb import calculate_bar_range


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
def test_calculate_bar_range_happy_path(test_data):
    """Test calculate_bar_range for up, down, and range trends."""
    index = pd.Timestamp("2024-01-01")
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [test_data["open"]],
        PriceLabel.HIGH: [test_data["high"]],
        PriceLabel.LOW: [test_data["low"]],
        PriceLabel.CLOSE: [test_data["close"]],
    }, index=[index])

    result = calculate_bar_range(price_data, current_bar_index=index)
    assert result == test_data["expected"], f"Failed for {test_data['description']}: expected {test_data['expected']}, got {result}"


def test_calculate_bar_range_success():
    """Test calculate_bar_range with valid data."""
    index = pd.Timestamp("2024-01-01")
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100],
        PriceLabel.HIGH: [110],
        PriceLabel.LOW: [95],
        PriceLabel.CLOSE: [105],
    }, index=[index])

    bar_size = calculate_bar_range(price_data, current_bar_index=index)
    assert bar_size == 15


def test_calculate_bar_range_invalid_index():
    """Test calculate_bar_range with invalid index."""
    index = pd.Timestamp("2024-01-01")
    invalid_index = pd.Timestamp("2024-01-02")
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100],
        PriceLabel.HIGH: [110],
        PriceLabel.LOW: [95],
        PriceLabel.CLOSE: [105],
    }, index=[index])

    with pytest.raises(IndexError):
        calculate_bar_range(price_data, current_bar_index=invalid_index)


def test_calculate_bar_range_missing_columns():
    """Test calculate_bar_range with missing price columns."""
    index = pd.Timestamp("2024-01-01")
    invalid_data = pd.DataFrame({
        PriceLabel.OPEN: [100],
        PriceLabel.CLOSE: [105],
    }, index=[index])

    with pytest.raises(KeyError):
        calculate_bar_range(invalid_data, current_bar_index=index)


def test_calculate_bar_range_correct_index():
    """Test that calculate_bar_range fetches the correct index from the DataFrame."""
    indices = pd.date_range('2024-01-01', periods=3)
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 101, 102],
        PriceLabel.HIGH: [110, 111, 112],
        PriceLabel.LOW: [95, 96, 97],
        PriceLabel.CLOSE: [105, 106, 107],
    }, index=indices)

    # Test first bar
    result = calculate_bar_range(price_data, current_bar_index=indices[0])
    assert result == 15

    # Test second bar
    result = calculate_bar_range(price_data, current_bar_index=indices[1])
    assert result == 15

    # Test third bar
    result = calculate_bar_range(price_data, current_bar_index=indices[2])
    assert result == 15 