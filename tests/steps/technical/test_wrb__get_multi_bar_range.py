"""Tests for _get_wide_range_bar functionality.

This module tests the wide range bar (WRB) detection functionality, which identifies
bars that show strong trend continuation. A WRB is defined as:

📈 For uptrend:
1. High > previous high
2. Low > previous low
3. Close > previous high

📉 For downtrend:
1. Low < previous low
2. High < previous high
3. Close < previous low

The implementation returns:
✅ For single bar WRBs: Only the last bar that meets all conditions
✅ For series WRBs: Only the last bar that meets all conditions
📏 Range: The difference between highest high and lowest low in the series
"""

import pandas as pd
import pytest

from src.models.base import PriceLabel
from src.steps.technical.wrb import _get_wide_range_bar


# region: _get_wide_range_bar
@pytest.mark.parametrize(
    "open, high, low, close, expected_range, description",
    [
        # Uptrend WRB cases
        (100, 110, 97, 109, 13, "single_bar_uptrend_wrb"),      # high (110) > prev high (106) AND low (97) > prev low (96) AND close (109) > prev high (106)
        
        # Downtrend WRB cases
        (110, 105, 85, 95, 20, "single_bar_downtrend_wrb"),     # low (85) < prev low (96) AND high (105) < prev high (106) AND close (95) < prev low (96)
    ]
)
def test_get_wide_range_bar_single_bar_wrb(open, high, low, close, expected_range, description):
    """Test _get_wide_range_bar for single bar WRB cases.
    
    These are cases where a single bar fully qualifies as a WRB:
    📈 Uptrend WRB:
      ✅ High > previous high
      ✅ Low > previous low
      ✅ Close > previous high
    
    📉 Downtrend WRB:
      ✅ Low < previous low
      ✅ High < previous high
      ✅ Close < previous low

    ⚠️ Note: A bar cannot be both uptrend and downtrend WRB at the same time.
    The implementation returns only the last bar that meets all conditions.
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
    range_size, wrb_indices = _get_wide_range_bar(price_data, indices[2])
    
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
                PriceLabel.LOW: [95, 97, 99, 101],      # Strictly increasing lows
                PriceLabel.CLOSE: [103, 105, 107, 110],  # Closes above previous highs
            }, index=pd.date_range('2024-01-01', periods=4)),
            10,  # Highest high (111) - Lowest low (101) = 10
            [pd.Timestamp('2024-01-04')],  # Only the last bar should be included
            "uptrend_series_wrb"
        ),
        (
            pd.DataFrame({
                PriceLabel.OPEN: [106, 104, 102, 100],
                PriceLabel.HIGH: [111, 109, 107, 105],  # Strictly decreasing highs
                PriceLabel.LOW: [101, 99, 97, 95],      # Strictly decreasing lows
                PriceLabel.CLOSE: [110, 108, 106, 94],  # Only last bar closes below previous low
            }, index=pd.date_range('2024-01-01', periods=4)),
            10,  # Highest high (105) - Lowest low (95) = 10
            [pd.Timestamp('2024-01-04')],  # Only the last bar should be included
            "downtrend_series_wrb"
        ),
    ]
)
def test_get_wide_range_bar_series_wrb(price_data, expected_range, expected_indices, description):
    """Test _get_wide_range_bar for series WRB cases.
    
    These are cases where multiple consecutive bars form a WRB series:
    📈 Uptrend series WRB:
      ✅ Each bar's high > previous high
      ✅ Each bar's low > previous low
      ✅ Each bar's close > previous high
    
    📉 Downtrend series WRB:
      ✅ Each bar's low < previous low
      ✅ Each bar's high < previous high
      ✅ Each bar's close < previous low

    The implementation returns only the last bar that meets all conditions,
    and calculates the range based on the highest high and lowest low in the series.
    """
    # Test the last bar
    range_size, wrb_indices = _get_wide_range_bar(price_data, price_data.index[-1])
    
    # For series WRB cases, we expect:
    # 1. Only the last bar to be included in indices
    # 2. Range size to match expected value
    assert list(wrb_indices) == list(expected_indices), f"Failed for {description}: expected indices {expected_indices}, got {wrb_indices}"
    assert range_size == expected_range, f"Failed for {description}: expected range {expected_range}, got {range_size}"


def test_get_wide_range_bar_one_bar_data_series():
    """Test _get_wide_range_bar for first bar edge case.
    
    First bar should never be considered a WRB because:
    ❌ No previous bar to compare against
    ❌ Cannot establish trend direction
    """
    # Create single bar of data
    indices = pd.date_range('2024-01-01', periods=1)
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100],
        PriceLabel.HIGH: [110],
        PriceLabel.LOW: [95],
        PriceLabel.CLOSE: [105],
    }, index=indices)

    range_size, wrb_indices = _get_wide_range_bar(price_data, indices[0])
    assert wrb_indices == [], "Expected no WRB indices for first bar"
    assert str(range_size) == 'nan', "Expected nan range size for first bar"


def test_get_wide_range_current_bar_not_part_of_wrb():
    """Test _get_wide_range_bar when WRB pattern occurs before current bar.
    
    This test case verifies behavior when:
    📈 Uptrend WRB pattern in bars 2-4:
      ✅ Bar 2: First WRB (high > prev high, low > prev low, close > prev high)
      ✅ Bar 3: Second WRB (high > prev high, low > prev low, close > prev high)
      ✅ Bar 4: Third WRB (high > prev high, low > prev low, close > prev high)
      ✅ Bar 5: Fourth WRB (high > prev high, low > prev low, close > prev high)
      ❌ Bar 6: Current bar (not part of pattern)
    
    The test verifies that:
    1. No WRB is detected for current bar
    2. Range is nan
    3. Indices list is empty
    """
    # Create 6 bars of data
    indices = pd.date_range('2024-01-01', periods=6)
    price_data = pd.DataFrame({
        PriceLabel.OPEN: [100, 102, 104, 106, 108, 110],
        PriceLabel.HIGH: [105, 107, 109, 111, 113, 106],  # Strictly increasing highs. Last high 106 is not series high
        PriceLabel.LOW: [95, 97, 99, 101, 103, 105],      # Strictly increasing lows
        PriceLabel.CLOSE: [103, 105, 107, 109, 111, 114],  # Closes above previous highs
    }, index=indices)

    # Test the last bar (index 5)
    range_size, wrb_indices = _get_wide_range_bar(price_data, indices[5])
    
    # For a pattern that occurred before current bar, we expect:
    # 1. No indices returned (empty list)
    # 2. Range size should be nan
    assert wrb_indices == [], "Expected no WRB indices for pattern before current bar"
    assert str(range_size) == 'nan', "Expected nan range size for pattern before current bar"


@pytest.mark.parametrize(
    "open, high, low, close, description",
    [
        (100, 110, 95, 105, "uptrend_close_below_prev_high"),      # up bar: high > prev high but close (105) <= prev high (106)
        (110, 106, 90, 97, "downtrend_close_above_prev_low"),     # down bar: low < prev low but close (97) >= prev low (96)
    ]
)
def test_get_wide_range_bar_non_wrb_cases_due_to_close_condition_unmet(open, high, low, close, description):
    """Test _get_wide_range_bar for cases that should NOT be identified as WRBs due to close condition not being met.
    
    These are cases where bars have the correct trend direction but don't meet the close condition:
    📈 Uptrend bar that doesn't close above previous high:
      ✅ High > previous high
      ❌ Close > previous high
    
    📉 Downtrend bar that doesn't close below previous low:
      ✅ Low < previous low
      ❌ Close < previous low

    ❌ No trend direction:
      ❌ High > previous high
      ❌ Low < previous low

    ⚠️ Unclear trend direction:
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
    range_size, wrb_indices = _get_wide_range_bar(price_data, indices[2])
    
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
        (100, 106, 96, 103, "equal_high"),      # high = prev high (106)
        (100, 105, 96, 103, "equal_low"),       # low = prev low (96)
    ]
)
def test_get_wide_range_bar_non_wrb_cases_due_to_new_extreme_condition_unmet(open, high, low, close, description):
    """Test _get_wide_range_bar for cases that should NOT be identified as WRBs due to no new extreme being made.
    
    These are cases where bars don't establish a trend direction because they don't make new extremes:
    ❌ No higher high case:
      ❌ High > previous high
      ❌ Low < previous low
    
    ❌ No lower low case:
      ❌ High > previous high
      ❌ Low < previous low

    ❌ Equal high case:
      ❌ High = previous high
      ❌ Cannot establish trend direction

    ❌ Equal low case:
      ❌ Low = previous low
      ❌ Cannot establish trend direction
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
    range_size, wrb_indices = _get_wide_range_bar(price_data, indices[2])
    
    # For non-WRB cases, we expect:
    # 1. No indices returned (empty list)
    # 2. Range size should be nan
    assert wrb_indices == [], f"Failed for {description}: expected no WRB indices, got {wrb_indices}"
    assert str(range_size) == 'nan', f"Failed for {description}: expected nan range size, got {range_size}"


# endregion 