"""Tests for wide range bar detection functionality."""

import pandas as pd
import pytest

from src.models.base import PriceLabel
from src.models.strategy import StrategyExecutionContext, StrategyStep
from src.steps.technical.wrb import (
    _get_bar_high_low_range,
    _validate_lookup_bars,
    detect_wide_range_bar,
)


@pytest.fixture
def sample_data():
    """Create sample price data for testing."""
    return pd.DataFrame({
        PriceLabel.OPEN: [100, 101, 102, 103, 104],
        PriceLabel.HIGH: [105, 106, 107, 108, 109],
        PriceLabel.LOW: [95, 96, 97, 98, 99],
        PriceLabel.CLOSE: [103, 104, 105, 106, 107]
    }, index=pd.date_range('2024-01-01', periods=5))


@pytest.fixture
def sample_step():
    """Create a sample strategy step for testing."""
    return StrategyStep(
        id="test_step_id",
        name="test_step",
        evaluation_fn=lambda x, y, z: None,
        description="Test step for unit testing",
        config={},
        reevaluates=[]
    )


@pytest.fixture
def sample_context(sample_step):
    """Create a sample strategy execution context."""
    return StrategyExecutionContext()


@pytest.mark.skip(reason="Skipping main function tests")
def test_detect_wide_range_bar_success(sample_data, sample_context):
    """Test successful detection of a wide range bar."""
    # Configure a wide range bar scenario
    sample_data.loc[sample_data.index[-1], PriceLabel.HIGH] = 120  # Make last bar wider
    sample_data.loc[sample_data.index[-1], PriceLabel.LOW] = 90
    
    result = detect_wide_range_bar(
        data=sample_data,
        context=sample_context,
        config={'lookback_bars': 3, 'min_size_increase_pct': 50.0}
    )
    
    assert result.is_success is True
    assert result.step_output['is_wide_range'] is True
    assert result.step_output['size_increase_pct'] > 50.0
    assert result.step_output['lookback_bars'] == 3
    assert result.step_output['min_size_increase_pct'] == 50.0


@pytest.mark.skip(reason="Skipping main function tests")
def test_detect_wide_range_bar_not_wide(sample_data, sample_context):
    """Test detection when bar is not wide enough."""
    result = detect_wide_range_bar(
        data=sample_data,
        context=sample_context,
        config={'lookback_bars': 3, 'min_size_increase_pct': 50.0}
    )
    
    assert result.is_success is True
    assert result.step_output['is_wide_range'] is False
    assert result.step_output['size_increase_pct'] < 50.0


@pytest.mark.skip(reason="Skipping main function tests")
def test_detect_wide_range_bar_insufficient_data(sample_data, sample_context):
    """Test handling of insufficient data."""
    result = detect_wide_range_bar(
        data=sample_data.iloc[:2],  # Only 2 bars
        context=sample_context,
        config={'lookback_bars': 3, 'min_size_increase_pct': 50.0}
    )
    
    assert result.is_success is False
    assert "Not enough bars" in result.message


@pytest.mark.skip(reason="Skipping main function tests")
def test_detect_wide_range_bar_empty_data(sample_context):
    """Test handling of empty data."""
    empty_data = pd.DataFrame(columns=[PriceLabel.OPEN, PriceLabel.HIGH, PriceLabel.LOW, PriceLabel.CLOSE])
    
    result = detect_wide_range_bar(
        data=empty_data,
        context=sample_context,
        config={'lookback_bars': 3, 'min_size_increase_pct': 50.0}
    )
    
    assert result.is_success is False
    assert "No data available" in result.message


@pytest.mark.skip(reason="Skipping main function tests")
def test_detect_wide_range_bar_zero_size(sample_data, sample_context):
    """Test handling of zero-sized bars."""
    # Make all bars have zero size
    sample_data[PriceLabel.HIGH] = sample_data[PriceLabel.LOW]
    
    result = detect_wide_range_bar(
        data=sample_data,
        context=sample_context,
        config={'lookback_bars': 3, 'min_size_increase_pct': 50.0}
    )
    
    assert result.is_success is False
    assert "average bar size is zero" in result.message


@pytest.mark.skip(reason="Skipping main function tests")
def test_detect_wide_range_bar_invalid_data(sample_context):
    """Test handling of invalid data format."""
    invalid_data = pd.DataFrame({'invalid': [1, 2, 3]})
    
    result = detect_wide_range_bar(
        data=invalid_data,
        context=sample_context,
        config={'lookback_bars': 3, 'min_size_increase_pct': 50.0}
    )
    
    assert result.is_success is False
    assert "Invalid price data format" in result.message


@pytest.mark.skip(reason="Skipping main function tests")
def test_detect_wide_range_bar_default_config(sample_data, sample_context):
    """Test detection with default configuration values."""
    # Configure a wide range bar scenario
    sample_data.loc[sample_data.index[-1], PriceLabel.HIGH] = 120
    sample_data.loc[sample_data.index[-1], PriceLabel.LOW] = 90
    
    result = detect_wide_range_bar(
        data=sample_data,
        context=sample_context,
        config={}  # Use default values
    )
    
    assert result.is_success is True
    assert result.step_output['lookback_bars'] == 20  # Default value
    assert result.step_output['min_size_increase_pct'] == 50.0  # Default value 


# region: _validate_lookup_bars

def test_validate_lookup_bars_success(sample_data):
    """Test successful validation of lookup bars."""
    result = _validate_lookup_bars(sample_data, lookback_bars=3)
    assert result is True


def test_validate_lookup_bars_empty_data():
    """Test validation with empty data."""
    empty_data = pd.DataFrame(columns=[PriceLabel.OPEN, PriceLabel.HIGH, PriceLabel.LOW, PriceLabel.CLOSE])
    with pytest.raises(ValueError, match="No data available"):
        _validate_lookup_bars(empty_data, lookback_bars=3)


def test_validate_lookup_bars_insufficient_data(sample_data):
    """Test validation with insufficient data."""
    with pytest.raises(ValueError, match="Not enough bars for lookback period"):
        _validate_lookup_bars(sample_data.iloc[:2], lookback_bars=3)


# endregion _validate_lookup_bars

# region: _get_bar_high_low_range
@pytest.mark.parametrize(
    "open_, high, low, close, description",
    [
        (100, 110, 95, 105, "uptrend"),      # up bar: close > open
        (110, 115, 90, 95, "downtrend"),     # down bar: close < open
        (100, 105, 95, 100, "range/sideways"), # range bar: close == open
    ]
)
def test_get_bar_high_low_range_happy_path(open_, high, low, close, description):
    """Test _get_bar_high_low_range for up, down, and range trends."""
    index = pd.Timestamp("2024-01-01")
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [open_],
        PriceLabel.HIGH: [high],
        PriceLabel.LOW: [low],
        PriceLabel.CLOSE: [close],
    }, index=[index])

    result = _get_bar_high_low_range(price_data, index)
    expected = abs(high - low)
    assert result == expected, f"Failed for {description}: expected {expected}, got {result}"


def test_get_bar_high_low_range_success(sample_data):
    """Test successful calculation of bar high-low range."""
    index = sample_data.index[0]
    bar_size = _get_bar_high_low_range(sample_data, index=index)
    expected_size = sample_data.loc[index][PriceLabel.HIGH] - sample_data.loc[index][PriceLabel.LOW]
    assert bar_size == expected_size


def test_get_bar_high_low_range_invalid_index(sample_data):
    """Test bar high-low range calculation with invalid index."""
    invalid_index = pd.Timestamp("2099-01-01")
    with pytest.raises(KeyError):
        _get_bar_high_low_range(sample_data, index=invalid_index)


def test_get_bar_high_low_range_missing_columns():
    """Test bar high-low range calculation with missing price columns."""
    invalid_data = pd.DataFrame({'invalid': [1, 2, 3]})
    index = invalid_data.index[0]
    with pytest.raises(KeyError):
        _get_bar_high_low_range(invalid_data, index=index)



# endregion _get_bar_high_low_range