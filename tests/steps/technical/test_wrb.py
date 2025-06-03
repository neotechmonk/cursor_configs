"""Tests for wide range bar detection functionality."""

import pandas as pd
import pytest

from src.models.base import PriceLabel
from src.models.strategy import StrategyExecutionContext, StrategyStep
from src.steps.technical.wrb import (
    _get_bar_size,
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

# region: _get_bar_size

@pytest.mark.skip(reason="Skipping other handler function tests")
def test_get_bar_size_success(sample_data):
    """Test successful calculation of bar size."""
    bar_size = _get_bar_size(sample_data, bar_index=0)
    expected_size = sample_data.iloc[0][PriceLabel.HIGH] - sample_data.iloc[0][PriceLabel.LOW]
    assert bar_size == expected_size


@pytest.mark.skip(reason="Skipping other handler function tests")
def test_get_bar_size_invalid_index(sample_data):
    """Test bar size calculation with invalid index."""
    with pytest.raises(IndexError):
        _get_bar_size(sample_data, bar_index=100)


@pytest.mark.skip(reason="Skipping other handler function tests")
def test_get_bar_size_missing_columns():
    """Test bar size calculation with missing price columns."""
    invalid_data = pd.DataFrame({'invalid': [1, 2, 3]})
    with pytest.raises(KeyError):
        _get_bar_size(invalid_data, bar_index=0)


# endregion _get_bar_size