"""Tests for _validate_lookup_bars function in wrb.py."""

import pandas as pd
import pytest

from src.steps.technical.wrb import _validate_lookup_bars


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
                "id": "valid lookback from latest bar"
            },
            id="valid lookback from latest bar"
        ),
        pytest.param(
            {
                "lookback_bars": 2,
                "lookback_start_idx": pd.Timestamp("2024-01-03"),
                "expected": True,
                "id": "valid lookback from middle bar"
            },
            id="valid lookback from middle bar"
        ),
        pytest.param(
            {
                "lookback_bars": 6,
                "lookback_start_idx": None,
                "expected": False,
                "id": "insufficient bars from latest"
            },
            id="insufficient bars from latest"
        ),
        pytest.param(
            {
                "lookback_bars": 3,
                "lookback_start_idx": pd.Timestamp("2024-01-02"),
                "expected": False,
                "id": "insufficient bars from middle"
            },
            id="insufficient bars from middle"
        ),
    ]
)
def test_validate_lookup_bars_happy_path(price_data, test_data):
    """Test _validate_lookup_bars with various valid scenarios."""
    result = _validate_lookup_bars(
        data=price_data,
        lookback_bars=test_data["lookback_bars"],
        lookback_start_idx=test_data["lookback_start_idx"]
    )
    assert result == test_data["expected"]


def test_validate_lookup_bars_empty_data():
    """Test _validate_lookup_bars with empty data."""
    empty_data = pd.DataFrame()
    with pytest.raises(ValueError, match="No data available"):
        _validate_lookup_bars(empty_data, lookback_bars=3)


def test_validate_lookup_bars_invalid_start_idx(price_data):
    """Test _validate_lookup_bars with invalid start index."""
    invalid_idx = pd.Timestamp("2099-01-01")
    with pytest.raises(IndexError, match=f"Lookback start index {invalid_idx} not found in data"):
        _validate_lookup_bars(price_data, lookback_bars=3, lookback_start_idx=invalid_idx) 