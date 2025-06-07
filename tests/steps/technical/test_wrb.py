"""Tests for wide range bar detection functionality."""

import pandas as pd
import pytest

from src.models.base import PriceLabel
from src.models.strategy import StrategyExecutionContext, StrategyStep
from src.steps.technical.wrb import (
    _get_wide_range_bar,
    _is_bar_wider_than_lookback,
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


# region: _get_wide_range_bar
def test_get_wide_range_bar_success(sample_data):
    """Test successful calculation of wide range bar."""
    result = _get_wide_range_bar(sample_data, sample_data.index[-1])
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], float)
    assert isinstance(result[1], list)


def test_get_wide_range_bar_invalid_index(sample_data):
    """Test behavior with invalid index."""
    invalid_index = pd.Timestamp("2099-01-01")
    with pytest.raises(IndexError, match=f"Current bar index {invalid_index} not found in data"):
        _get_wide_range_bar(sample_data, invalid_index)


def test_get_wide_range_bar_missing_columns(sample_data):
    """Test behavior with missing price columns."""
    data = sample_data.drop(columns=[PriceLabel.HIGH])
    with pytest.raises(KeyError, match=PriceLabel.HIGH):
        _get_wide_range_bar(data, sample_data.index[-1])


def test_get_wide_range_bar_first_bar(sample_data):
    """Test behavior with first bar."""
    result = _get_wide_range_bar(sample_data, sample_data.index[0])
    assert result[0] == float('nan')
    assert result[1] == []


def test_get_wide_range_bar_no_trend(sample_data):
    """Test behavior with no trend."""
    # Create data with no clear trend
    data = sample_data.copy()
    data.loc[data.index[1], PriceLabel.HIGH] = data.loc[data.index[0], PriceLabel.HIGH]
    data.loc[data.index[1], PriceLabel.LOW] = data.loc[data.index[0], PriceLabel.LOW]
    data.loc[data.index[1], PriceLabel.CLOSE] = data.loc[data.index[0], PriceLabel.HIGH]
    
    result = _get_wide_range_bar(data, data.index[1])
    assert result[0] == float('nan')
    assert result[1] == []


def test_get_wide_range_bar_uptrend(sample_data):
    """Test behavior with uptrend."""
    # Create data with clear uptrend
    data = sample_data.copy()
    data.loc[data.index[1], PriceLabel.HIGH] = data.loc[data.index[0], PriceLabel.HIGH] + 1
    data.loc[data.index[1], PriceLabel.LOW] = data.loc[data.index[0], PriceLabel.LOW] + 1
    data.loc[data.index[1], PriceLabel.CLOSE] = data.loc[data.index[0], PriceLabel.HIGH] + 1
    
    result = _get_wide_range_bar(data, data.index[1])
    assert result[0] > 0
    assert len(result[1]) > 0


def test_get_wide_range_bar_downtrend(sample_data):
    """Test behavior with downtrend."""
    # Create data with clear downtrend
    data = sample_data.copy()
    data.loc[data.index[1], PriceLabel.HIGH] = data.loc[data.index[0], PriceLabel.HIGH] - 1
    data.loc[data.index[1], PriceLabel.LOW] = data.loc[data.index[0], PriceLabel.LOW] - 1
    data.loc[data.index[1], PriceLabel.CLOSE] = data.loc[data.index[0], PriceLabel.LOW] - 1
    
    result = _get_wide_range_bar(data, data.index[1])
    assert result[0] > 0
    assert len(result[1]) > 0
# endregion


# region: _is_bar_wider_than_lookback
def test_is_bar_wider_than_lookback_success(sample_data):
    """Test successful comparison of bar width."""
    result = _is_bar_wider_than_lookback(
        sample_data,
        sample_data.index[-1],
        lookback_bars=3,
        min_size_increase_pct=0.5
    )
    assert isinstance(result, bool)


def test_is_bar_wider_than_lookback_invalid_index(sample_data):
    """Test behavior with invalid index."""
    invalid_index = pd.Timestamp("2099-01-01")
    with pytest.raises(IndexError, match=f"Current bar index {invalid_index} not found in data"):
        _is_bar_wider_than_lookback(
            sample_data,
            invalid_index,
            lookback_bars=3,
            min_size_increase_pct=0.5
        )


def test_is_bar_wider_than_lookback_missing_columns(sample_data):
    """Test behavior with missing price columns."""
    data = sample_data.drop(columns=[PriceLabel.HIGH])
    with pytest.raises(KeyError, match=PriceLabel.HIGH):
        _is_bar_wider_than_lookback(
            data,
            sample_data.index[-1],
            lookback_bars=3,
            min_size_increase_pct=0.5
        )


def test_is_bar_wider_than_lookback_insufficient_bars(sample_data):
    """Test behavior with insufficient lookback bars."""
    result = _is_bar_wider_than_lookback(
        sample_data,
        sample_data.index[1],  # Only 1 bar before this
        lookback_bars=3,
        min_size_increase_pct=0.5
    )
    assert result is False


def test_is_bar_wider_than_lookback_zero_reference(sample_data):
    """Test behavior when reference size is zero."""
    # Create data where all bars have same high and low
    data = sample_data.copy()
    data[PriceLabel.HIGH] = 100
    data[PriceLabel.LOW] = 100
    
    with pytest.raises(ZeroDivisionError, match="Reference size is zero"):
        _is_bar_wider_than_lookback(
            data,
            data.index[-1],
            lookback_bars=3,
            min_size_increase_pct=0.5
        )


def test_is_bar_wider_than_lookback_invalid_method(sample_data):
    """Test behavior with invalid comparison method."""
    with pytest.raises(ValueError, match="Invalid comparison method"):
        _is_bar_wider_than_lookback(
            sample_data,
            sample_data.index[-1],
            lookback_bars=3,
            min_size_increase_pct=0.5,
            comparison_method="invalid"
        )
# endregion


# region: _get_wrb_series_range


def test_wrb_series_range_single_bar():
    """Test that function returns correct range for a single bar."""
    # Single bar with high=110, low=90
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100],
        PriceLabel.HIGH: [110],
        PriceLabel.LOW: [90],
        PriceLabel.CLOSE: [105],
    }, index=pd.date_range('2024-01-01', periods=1))
    
    idx = price_data.index[0]
    range_size, indices = _get_multi_bar_range(price_data, idx)
    
    assert range_size == 20  # 110 - 90
    assert indices == [idx]


def test_wrb_series_range_uptrending_multiple_bars():
    """Test that function correctly identifies a series of bars in an uptrend."""
    # Series of bars where each high is higher than previous
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 102, 104, 106],
        PriceLabel.HIGH: [105, 107, 109, 111],  # Strictly increasing highs
        PriceLabel.LOW: [95, 97, 99, 101],
        PriceLabel.CLOSE: [103, 105, 107, 109],
    }, index=pd.date_range('2024-01-01', periods=4))
    
    idx = price_data.index[-1]  # Last bar
    range_size, indices = _get_multi_bar_range(price_data, idx)
    
    assert range_size == 16  # Highest high (111) - Lowest low (95)
    assert len(indices) == 4  # All 4 bars should be included
    assert indices == list(price_data.index)


def test_wrb_series_range_uptrending_break_in_series():
    """Test that function stops when uptrend breaks."""
    # Series where third bar breaks the trend
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 102, 104, 106],
        PriceLabel.HIGH: [105, 107, 106, 108],  # Third bar's high is lower than previous
        PriceLabel.LOW: [95, 97, 99, 101],
        PriceLabel.CLOSE: [103, 105, 107, 109],
    }, index=pd.date_range('2024-01-01', periods=4))
    
    idx = price_data.index[-1]  # Last bar
    range_size, indices = _get_multi_bar_range(price_data, idx)
    
    assert range_size == 9  # Highest high (108) - Lowest low (99)
    assert len(indices) == 2  # Only last two bars should be included
    assert indices == list(price_data.index[-2:])


def test_wrb_series_range_invalid_index():
    """Test that function raises IndexError for invalid index."""
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100],
        PriceLabel.HIGH: [110],
        PriceLabel.LOW: [90],
        PriceLabel.CLOSE: [105],
    }, index=pd.date_range('2024-01-01', periods=1))
    
    with pytest.raises(IndexError):
        _get_multi_bar_range(price_data, pd.Timestamp('2099-01-01'))


def test_wrb_series_range_missing_columns():
    """Test that function raises KeyError for missing price columns."""
    price_data = pd.DataFrame({
        'invalid': [1, 2, 3],
    }, index=pd.date_range('2024-01-01', periods=3))
    
    with pytest.raises(KeyError):
        _get_multi_bar_range(price_data, price_data.index[0])

# endregion _get_wrb_series_range


def test_wrb_series_range_downtrending_multiple_bars():
    """Test that function correctly identifies a series of bars in a downtrend."""
    # Series of bars where each low is lower than previous
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [106, 104, 102, 100],
        PriceLabel.HIGH: [111, 109, 107, 105],
        PriceLabel.LOW: [101, 99, 97, 95],  # Strictly decreasing lows
        PriceLabel.CLOSE: [103, 101, 99, 97],  # Closes below previous lows
    }, index=pd.date_range('2024-01-01', periods=4))
    
    idx = price_data.index[-1]  # Last bar
    range_size, indices = _get_multi_bar_range(price_data, idx)
    
    assert range_size == 16  # Highest high (111) - Lowest low (95)
    assert len(indices) == 4  # All 4 bars should be included
    assert indices == list(price_data.index)


def test_wrb_series_range_mixed_trends():
    """Test that function correctly identifies a series of bars with mixed trends."""
    # Series of bars that alternate between uptrend and downtrend
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 102, 98, 96],
        PriceLabel.HIGH: [105, 107, 103, 101],  # First two bars uptrend, last two downtrend
        PriceLabel.LOW: [95, 97, 93, 91],
        PriceLabel.CLOSE: [103, 107, 93, 91],  # Closes above previous high for uptrend, below previous low for downtrend
    }, index=pd.date_range('2024-01-01', periods=4))
    
    idx = price_data.index[-1]  # Last bar
    range_size, indices = _get_multi_bar_range(price_data, idx)
    
    assert range_size == 16  # Highest high (107) - Lowest low (91)
    assert len(indices) == 4  # All 4 bars should be included
    assert indices == list(price_data.index)