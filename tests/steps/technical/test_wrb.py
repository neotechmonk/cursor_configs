"""Tests for wide range bar detection functionality."""

import pandas as pd
import pytest

from src.models.base import PriceLabel
from src.models.strategy import StrategyExecutionContext, StrategyStep
from src.steps.technical.range import _get_multi_bar_range
from src.steps.technical.wrb import (
    _get_bar_high_low_range,
    _is_bar_wider_than_lookback,
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
    "open, high, low, close, expected, description",
    [
        (100, 110, 95, 105, 15, "uptrend"),      # up bar: close > open
        (110, 115, 90, 95, 25, "downtrend"),     # down bar: close < open
        (100, 105, 95, 100, 10, "range/sideways"), # range bar: close == open
    ]
)
def test_get_bar_high_low_range_happy_path(open, high, low, close, expected, description):
    """Test _get_bar_high_low_range for up, down, and range trends."""
    index = pd.Timestamp("2024-01-01")
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [open],
        PriceLabel.HIGH: [high],
        PriceLabel.LOW: [low],
        PriceLabel.CLOSE: [close],
    }, index=[index])

    result = _get_bar_high_low_range(price_data, index)
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


def test_get_bar_high_low_range_correct_index():
    """Test that _get_bar_high_low_range fetches the correct index from the DataFrame."""
    indices = pd.date_range(start='2024-01-01', periods=3)
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 101, 102],
        PriceLabel.HIGH: [110, 111, 112],
        PriceLabel.LOW: [95, 96, 97],
        PriceLabel.CLOSE: [105, 106, 107],
    }, index=indices)

    # Test fetching the first index
    result = _get_bar_high_low_range(price_data, indices[0])
    expected = 15  # high - low = 110 - 95 = 15
    assert result == expected, f"Failed to fetch correct index: expected {expected}, got {result}"

    # Test fetching the second index
    result = _get_bar_high_low_range(price_data, indices[1])
    expected = 15  # high - low = 111 - 96 = 15
    assert result == expected, f"Failed to fetch correct index: expected {expected}, got {result}"

    # Test fetching the third index
    result = _get_bar_high_low_range(price_data, indices[2])
    expected = 15  # high - low = 112 - 97 = 15
    assert result == expected, f"Failed to fetch correct index: expected {expected}, got {result}"


# endregion _get_bar_high_low_range

# region: _is_bar_wider_than_lookback

def test_is_bar_wider_than_lookback_true():
    """Test that function detects a bar wider than lookback by required percentage."""
    # Last bar is much wider
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 100, 100, 100],
        PriceLabel.HIGH: [105, 105, 105, 120],
        PriceLabel.LOW: [95, 95, 95, 90],
        PriceLabel.CLOSE: [103, 104, 105, 110],
    }, index=pd.date_range('2024-01-01', periods=4))
    idx = price_data.index[-1]
    is_wide = _is_bar_wider_than_lookback(price_data, idx, 3, 0.5)  # 50% = 0.5
    assert is_wide


def test_is_bar_wider_than_lookback_false():
    """Test that function detects a bar NOT wider than lookback by required percentage."""
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 100, 100, 100],
        PriceLabel.HIGH: [105, 105, 105, 106],
        PriceLabel.LOW: [95, 95, 95, 96],
        PriceLabel.CLOSE: [103, 104, 105, 100],
    }, index=pd.date_range('2024-01-01', periods=4))
    idx = price_data.index[-1]
    is_wide = _is_bar_wider_than_lookback(price_data, idx, 3, 0.5)  # 50% = 0.5
    assert not is_wide


def test_is_bar_wider_than_lookback_zero_division():
    """Test that ZeroDivisionError is raised if lookback bars have zero size."""
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 100, 100, 100],
        PriceLabel.HIGH: [100, 100, 100, 120],
        PriceLabel.LOW: [100, 100, 100, 90],
        PriceLabel.CLOSE: [100, 100, 100, 110],
    }, index=pd.date_range('2024-01-01', periods=4))
    idx = price_data.index[-1]
    with pytest.raises(ZeroDivisionError):
        _is_bar_wider_than_lookback(price_data, idx, 3, 50.0)


def test_is_bar_wider_than_lookback_empty_lookback():
    """Test that function returns False if lookback is empty."""
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100],
        PriceLabel.HIGH: [105],
        PriceLabel.LOW: [95],
        PriceLabel.CLOSE: [103],
    }, index=pd.date_range('2024-01-01', periods=1))
    idx = price_data.index[0]
    is_wide = _is_bar_wider_than_lookback(price_data, idx, 1, 0.5)  # 50% = 0.5
    assert not is_wide


def test_is_bar_wider_than_lookback_index_error():
    """Test that KeyError is raised if current_bar_index is not in the DataFrame index."""
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 100, 100],
        PriceLabel.HIGH: [105, 105, 105],
        PriceLabel.LOW: [95, 95, 95],
        PriceLabel.CLOSE: [103, 104, 105],
    }, index=pd.date_range('2024-01-01', periods=3))
    with pytest.raises(KeyError):
        _is_bar_wider_than_lookback(price_data, pd.Timestamp('2099-01-01'), 2, 50.0)


def test_is_bar_wider_than_lookback_max_method():
    """Test that function detects a bar wider than max lookback by required percentage."""
    # Last bar is wider than max of lookback
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 100, 100, 100],
        PriceLabel.HIGH: [105, 110, 105, 120],  # Max in lookback is 110
        PriceLabel.LOW: [95, 95, 95, 90],
        PriceLabel.CLOSE: [103, 104, 105, 110],
    }, index=pd.date_range('2024-01-01', periods=4))
    idx = price_data.index[-1]
    is_wide = _is_bar_wider_than_lookback(price_data, idx, 3, 0.5, comparison_method="max")  # 50% = 0.5
    assert is_wide


def test_is_bar_wider_than_lookback_avg_method():
    """Test that function detects a bar wider than average lookback by required percentage."""
    # Last bar is wider than average of lookback
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 100, 100, 100],
        PriceLabel.HIGH: [105, 105, 105, 120],  # Avg in lookback is 105
        PriceLabel.LOW: [95, 95, 95, 90],
        PriceLabel.CLOSE: [103, 104, 105, 110],
    }, index=pd.date_range('2024-01-01', periods=4))
    idx = price_data.index[-1]
    is_wide = _is_bar_wider_than_lookback(price_data, idx, 3, 0.5, comparison_method="avg")  # 50% = 0.5
    assert is_wide


def test_is_bar_wider_than_lookback_invalid_method():
    """Test that function raises ValueError for invalid comparison method."""
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 100, 100],
        PriceLabel.HIGH: [105, 105, 105],
        PriceLabel.LOW: [95, 95, 95],
        PriceLabel.CLOSE: [103, 104, 105],
    }, index=pd.date_range('2024-01-01', periods=3))
    idx = price_data.index[-1]
    
    with pytest.raises(ValueError, match="Invalid comparison method"):
        _is_bar_wider_than_lookback(price_data, idx, 2, 0.5, comparison_method="invalid")

# endregion _is_bar_wider_than_lookback

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