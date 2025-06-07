"""Tests for validate_lookback_period function in wrb.py."""

import pandas as pd
import pytest

from src.steps.technical.wrb import validate_lookback_period


@pytest.fixture
def price_data():
    """Create sample price data for testing."""
    return pd.DataFrame(
        {
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [102, 103, 104, 105, 106]
        },
        index=pd.date_range('2024-01-01', periods=5)
    )


@pytest.mark.parametrize(
    "test_data",
    [
        pytest.param(
            {
                "lookback_bars": 3,
                "lookback_start_idx": None,
                "expected": True,
                "description": "valid lookback with default start index"
            },
            id="valid_default_start"
        ),
        pytest.param(
            {
                "lookback_bars": 3,
                "lookback_start_idx": pd.Timestamp('2024-01-04'),
                "expected": True,
                "description": "valid lookback with explicit start index"
            },
            id="valid_explicit_start"
        ),
        pytest.param(
            {
                "lookback_bars": 5,
                "lookback_start_idx": None,
                "expected": False,
                "description": "insufficient bars for lookback"
            },
            id="insufficient_bars"
        ),
        pytest.param(
            {
                "lookback_bars": 3,
                "lookback_start_idx": pd.Timestamp('2024-01-02'),
                "expected": False,
                "description": "insufficient bars before start index"
            },
            id="insufficient_bars_before_start"
        ),
    ]
)
def test_validate_lookback_period_happy_path(price_data, test_data):
    """Test validate_lookback_period with various valid scenarios."""
    result = validate_lookback_period(
        data=price_data,
        lookback_bars=test_data["lookback_bars"],
        lookback_start_idx=test_data["lookback_start_idx"]
    )
    assert result == test_data["expected"], f"Failed for {test_data['description']}: expected {test_data['expected']}, got {result}"


def test_validate_lookback_period_empty_data():
    """Test validate_lookback_period with empty data."""
    empty_data = pd.DataFrame()
    with pytest.raises(ValueError, match="No data available"):
        validate_lookback_period(empty_data, lookback_bars=3)


def test_validate_lookback_period_invalid_start_idx(price_data):
    """Test validate_lookback_period with invalid start index."""
    invalid_idx = pd.Timestamp('2099-01-01')
    with pytest.raises(IndexError, match=f"Lookback start index {invalid_idx} not found in data"):
        validate_lookback_period(price_data, lookback_bars=3, lookback_start_idx=invalid_idx) 