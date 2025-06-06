"""Tests for _get_multi_bar_range functionality."""

import pandas as pd
import pytest

from src.models.base import PriceLabel
from src.steps.technical.wrb import _get_multi_bar_range


# region: _get_multi_bar_range
@pytest.mark.parametrize(
    "open, high, low, close, expected_range, description",
    [
        (100, 110, 95, 111, 15, "single_bar_uptrend_wrb"),      # single bar: high (110) > prev high (106) AND close (111) >= prev high (106)
        (110, 106, 85, 95, 21, "single_bar_downtrend_wrb"),     # single bar: low (85) < prev low (96) AND close (95) <= prev low (96)
        (110, 115, 85, 111, 30, "single_bar_uptrend_wrb"),      # single bar: high (115) > prev high (106) AND close (111) >= prev high (106)
        (110, 106, 90, 95, 16, "single_bar_downtrend_wrb"),     # single bar: low (90) < prev low (96) AND close (95) <= prev low (96)
        (110, 106, 85, 96, 21, "single_bar_downtrend_wrb"),     # single bar: low (85) < prev low (96) AND close (96) <= prev low (96)
    ]
)
def test_get_multi_bar_range_single_bar_wrb(open, high, low, close, expected_range, description):
    """Test _get_multi_bar_range for single bar WRB cases.
    
    These are cases where a single bar fully qualifies as a WRB:
    - Uptrend WRB:
      ✅ High > previous high
      ✅ Close >= previous high
    
    - Downtrend WRB:
      ✅ Low < previous low
      ✅ Close <= previous low

    Note: A bar cannot be both uptrend and downtrend WRB at the same time.
    """
    # Create 3 bars of data
    indices = pd.date_range('2024-01-01', periods=3)
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 101, open],
        PriceLabel.HIGH: [105, 106, high],
        PriceLabel.LOW: [95, 96, low],
        PriceLabel.CLOSE: [103, 104, close],
    }, index=indices)

    # Test the last bar (index 2)
    range_size, wrb_indices = _get_multi_bar_range(price_data, indices[2])
    
    # For single bar WRB cases, we expect:
    # 1. Only the last bar to be included in indices
    # 2. Range size to match expected value
    assert wrb_indices == [indices[2]], f"Failed for {description}: expected only last bar in WRB indices"
    assert range_size == expected_range, f"Failed for {description}: expected range {expected_range}, got {range_size}"


@pytest.mark.parametrize(
    "price_data, expected_range, expected_indices, description",
    [
        (
            pd.DataFrame({
                PriceLabel.OPEN: [100, 102, 104, 106],
                PriceLabel.HIGH: [105, 107, 109, 111],  # Strictly increasing highs
                PriceLabel.LOW: [95, 97, 99, 101],
                PriceLabel.CLOSE: [103, 105, 107, 110],  # Closes above or equals previous highs
            }, index=pd.date_range('2024-01-01', periods=4)),
            14,  # Highest high (111) - Lowest low (97) = 14
            pd.date_range('2024-01-02', periods=3),  # Last 3 bars should be included (excluding first bar)
            "uptrend_series_wrb"
        ),
        (
            pd.DataFrame({
                PriceLabel.OPEN: [106, 104, 102, 100],
                PriceLabel.HIGH: [111, 109, 107, 105],
                PriceLabel.LOW: [101, 99, 97, 95],  # Strictly decreasing lows
                PriceLabel.CLOSE: [103, 101, 99, 95],  # Closes below or equals previous lows
            }, index=pd.date_range('2024-01-01', periods=4)),
            14,  # Highest high (109) - Lowest low (95) = 14
            pd.date_range('2024-01-02', periods=3),  # Last 3 bars should be included (excluding first bar)
            "downtrend_series_wrb"
        ),
    ]
)
def test_get_multi_bar_range_series_wrb(price_data, expected_range, expected_indices, description):
    """Test _get_multi_bar_range for series WRB cases.
    
    These are cases where multiple consecutive bars form a WRB series:
    - Uptrend series WRB:
      ✅ Each bar's high > previous high
      ✅ Each bar's close > previous high
    
    - Downtrend series WRB:
      ✅ Each bar's low < previous low
      ✅ Each bar's close < previous low
    """
    # Test the last bar
    range_size, wrb_indices = _get_multi_bar_range(price_data, price_data.index[-1])
    
    # For series WRB cases, we expect:
    # 1. All bars in the series to be included in indices (except the first bar)
    # 2. Range size to match expected value
    assert list(wrb_indices) == list(expected_indices), f"Failed for {description}: expected indices {expected_indices}, got {wrb_indices}"
    assert range_size == expected_range, f"Failed for {description}: expected range {expected_range}, got {range_size}"


@pytest.mark.parametrize(
    "open, high, low, close, description",
    [
        (100, 110, 95, 105, "uptrend_close_below_prev_high"),      # up bar: high > prev high but close (105) < prev high (106)
        (110, 106, 90, 97, "downtrend_close_above_prev_low"),     # down bar: low < prev low but close (97) > prev low (96)
        (110, 106, 85, 97, "no_trend_direction"),            # neither high > prev high nor low < prev low
        (110, 115, 85, 97, "unclear_trend_direction"),       # both high > prev high AND low < prev low, unclear direction
    ]
)
def test_get_multi_bar_range_non_wrb_cases_due_to_close_condition_unmet(open, high, low, close, description):
    """Test _get_multi_bar_range for cases that should NOT be identified as WRBs due to close condition not being met.
    
    These are cases where bars have the correct trend direction but don't meet the close condition:
    - Uptrend bar that doesn't close above previous high:
      ✅ High > previous high
      ❌ Close >= previous high
    
    - Downtrend bar that doesn't close below previous low:
      ✅ Low < previous low
      ❌ Close <= previous low

    - No trend direction:
      ❌ High > previous high
      ❌ Low < previous low

    - Unclear trend direction:
      ✅ High > previous high
      ✅ Low < previous low
      ❌ Close doesn't meet either condition
    """
    # Create 3 bars of data
    indices = pd.date_range('2024-01-01', periods=3)
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 101, open],
        PriceLabel.HIGH: [105, 106, high],
        PriceLabel.LOW: [95, 96, low],
        PriceLabel.CLOSE: [103, 104, close],
    }, index=indices)

    # Test the last bar (index 2)
    range_size, wrb_indices = _get_multi_bar_range(price_data, indices[2])
    
    # For non-WRB cases, we expect:
    # 1. No indices returned (empty list)
    # 2. Range size should be nan
    assert wrb_indices == [], f"Failed for {description}: expected no WRB indices, got {wrb_indices}"
    assert str(range_size) == 'nan', f"Failed for {description}: expected nan range size, got {range_size}"


@pytest.mark.parametrize(
    "open, high, low, close, description",
    [
        (100, 105, 95, 103, "no_higher_high"),      # high (105) <= prev high (106), no trend direction
        (110, 115, 97, 95, "no_lower_low"),     # low (97) >= prev low (96), no trend direction
    ]
)
def test_get_multi_bar_range_non_wrb_cases_due_to_new_extreme_condition_unmet(open, high, low, close, description):
    """Test _get_multi_bar_range for cases that should NOT be identified as WRBs due to no new extreme being made.
    
    These are cases where bars don't establish a trend direction because they don't make new extremes:
    - No higher high case:
      ❌ High > previous high
      ❌ Low < previous low
    
    - No lower low case:
      ❌ High > previous high
      ❌ Low < previous low
    """
    # Create 3 bars of data
    indices = pd.date_range('2024-01-01', periods=3)
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 101, open],
        PriceLabel.HIGH: [105, 106, high],
        PriceLabel.LOW: [95, 96, low],
        PriceLabel.CLOSE: [103, 104, close],
    }, index=indices)

    # Test the last bar (index 2)
    range_size, wrb_indices = _get_multi_bar_range(price_data, indices[2])
    
    # For non-WRB cases, we expect:
    # 1. No indices returned (empty list)
    # 2. Range size should be nan
    assert wrb_indices == [], f"Failed for {description}: expected no WRB indices, got {wrb_indices}"
    assert str(range_size) == 'nan', f"Failed for {description}: expected nan range size, got {range_size}"

# endregion 