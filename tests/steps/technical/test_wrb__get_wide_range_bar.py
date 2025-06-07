"""Tests for identify_wide_range_bar functionality.

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
from src.steps.technical.wrb import identify_wide_range_bar


# region: identify_wide_range_bar : specific cases
@pytest.mark.parametrize(
    "open, high, low, close, expected_range, description",
    [
        # Uptrend WRB cases
        (100, 110, 97, 109, 13, "single_bar_uptrend_wrb"),      # high (110) > prev high (106) AND low (97) > prev low (96) AND close (109) > prev high (106)
        
        # Downtrend WRB cases
        (110, 105, 85, 95, 20, "single_bar_downtrend_wrb"),     # low (85) < prev low (96) AND high (105) < prev high (106) AND close (95) < prev low (96)
    ]
)
def test_identify_wide_range_bar_single_bar_wrb(open, high, low, close, expected_range, description):
    """Test identify_wide_range_bar for single bar WRB cases.
    
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
    range_size, wrb_indices = identify_wide_range_bar(price_data, indices[2])
    
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
def test_identify_wide_range_bar_series_wrb(price_data, expected_range, expected_indices, description):
    """Test identify_wide_range_bar for series WRB cases.
    
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
    range_size, wrb_indices = identify_wide_range_bar(price_data, price_data.index[-1])
    
    # For series WRB cases, we expect:
    # 1. Only the last bar to be included in indices
    # 2. Range size to match expected value
    assert list(wrb_indices) == list(expected_indices), f"Failed for {description}: expected indices {expected_indices}, got {wrb_indices}"
    assert range_size == expected_range, f"Failed for {description}: expected range {expected_range}, got {range_size}"


def test_identify_wide_range_bar_one_bar_data_series():
    """Test identify_wide_range_bar for first bar edge case.
    
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

    range_size, wrb_indices = identify_wide_range_bar(price_data, indices[0])
    assert wrb_indices == [], "Expected no WRB indices for first bar"
    assert str(range_size) == 'nan', "Expected nan range size for first bar"


def test_identify_wide_range_bar_current_bar_not_part_of_wrb():
    """Test identify_wide_range_bar when WRB pattern occurs before current bar.
    
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
    range_size, wrb_indices = identify_wide_range_bar(price_data, indices[5])
    
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
def test_identify_wide_range_bar_non_wrb_cases_due_to_close_condition_unmet(open, high, low, close, description):
    """Test identify_wide_range_bar for cases that should NOT be identified as WRBs due to close condition not being met.
    
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
    range_size, wrb_indices = identify_wide_range_bar(price_data, indices[2])
    
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
def test_identify_wide_range_bar_non_wrb_cases_due_to_new_extreme_condition_unmet(open, high, low, close, description):
    """Test identify_wide_range_bar for cases that should NOT be identified as WRBs due to no new extreme being made.
    
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
    range_size, wrb_indices = identify_wide_range_bar(price_data, indices[2])
    
    # For non-WRB cases, we expect:
    # 1. No indices returned (empty list)
    # 2. Range size should be nan
    assert wrb_indices == [], f"Failed for {description}: expected no WRB indices, got {wrb_indices}"
    assert str(range_size) == 'nan', f"Failed for {description}: expected nan range size, got {range_size}"


# endregion 

# region: identify_wide_range_bar : comprehensive tests
@pytest.mark.skip(reason="Optional : covered by specific tests")
@pytest.mark.parametrize(
    "test_data, expected_range, expected_indices, description",
    [
        # Single Bar Tests
        pytest.param(
            {
                "type": "single",
                "data": {
                    "high": [105, 106, 110],
                    "low": [95, 96, 97],
                    "close": [103, 104, 109]
                }
            },
            13.0,
            ["2024-01-03 00:00:00"],
            """
            Pattern: Valid Uptrend WRB
            HIGH > prev HIGH: ✅ (110 > 106)
            LOW > prev LOW: ✅ (97 > 96)
            CLOSE > prev HIGH: ✅ (109 > 106)
            """,
            id="single_uptrend_wrb"
        ),
        pytest.param(
            {
                "type": "single",
                "data": {
                    "high": [105, 106, 105],
                    "low": [95, 96, 85],
                    "close": [103, 104, 95]
                }
            },
            20.0,
            ["2024-01-03 00:00:00"],
            """
            Pattern: Valid Downtrend WRB
            HIGH < prev HIGH: ✅ (105 < 106)
            LOW < prev LOW: ✅ (85 < 96)
            CLOSE < prev LOW: ✅ (95 < 96)
            """,
            id="single_downtrend_wrb"
        ),
        pytest.param(
            {
                "type": "single",
                "data": {
                    "high": [105, 106, 110],
                    "low": [95, 96, 97],
                    "close": [103, 104, 105]
                }
            },
            float('nan'),
            [],
            """
            Pattern: Uptrend Close Condition Fail
            HIGH > prev HIGH: ✅ (110 > 106)
            LOW > prev LOW: ✅ (97 > 96)
            CLOSE > prev HIGH: ❌ (105 <= 106)
            """,
            id="single_uptrend_close_fail"
        ),
        pytest.param(
            {
                "type": "single",
                "data": {
                    "high": [105, 106, 105],
                    "low": [95, 96, 85],
                    "close": [103, 104, 97]
                }
            },
            float('nan'),
            [],
            """
            Pattern: Downtrend Close Condition Fail
            HIGH < prev HIGH: ✅ (105 < 106)
            LOW < prev LOW: ✅ (85 < 96)
            CLOSE < prev LOW: ❌ (97 >= 96)
            """,
            id="single_downtrend_close_fail"
        ),
        pytest.param(
            {
                "type": "single",
                "data": {
                    "high": [105, 106, 105],
                    "low": [95, 96, 97],
                    "close": [103, 104, 104]
                }
            },
            float('nan'),
            [],
            """
            Pattern: No New High
            HIGH > prev HIGH: ❌ (105 <= 106)
            LOW > prev LOW: ✅ (97 > 96)
            CLOSE > prev HIGH: ❌ (104 <= 106)
            """,
            id="single_no_new_high"
        ),
        pytest.param(
            {
                "type": "single",
                "data": {
                    "high": [105, 106, 107],
                    "low": [95, 96, 96],
                    "close": [103, 104, 105]
                }
            },
            float('nan'),
            [],
            """
            Pattern: No New Low
            HIGH > prev HIGH: ✅ (107 > 106)
            LOW > prev LOW: ❌ (96 <= 96)
            CLOSE > prev HIGH: ❌ (105 <= 106)
            """,
            id="single_no_new_low"
        ),
        pytest.param(
            {
                "type": "single",
                "data": {
                    "high": [105, 106, 106],
                    "low": [95, 96, 97],
                    "close": [103, 104, 105]
                }
            },
            float('nan'),
            [],
            """
            Pattern: Equal High
            HIGH > prev HIGH: ❌ (106 = 106)
            LOW > prev LOW: ✅ (97 > 96)
            CLOSE > prev HIGH: ❌ (105 <= 106)
            """,
            id="single_equal_high"
        ),
        pytest.param(
            {
                "type": "single",
                "data": {
                    "high": [105, 106, 107],
                    "low": [95, 96, 96],
                    "close": [103, 104, 105]
                }
            },
            float('nan'),
            [],
            """
            Pattern: Equal Low
            HIGH > prev HIGH: ✅ (107 > 106)
            LOW > prev LOW: ❌ (96 = 96)
            CLOSE > prev HIGH: ❌ (105 <= 106)
            """,
            id="single_equal_low"
        ),
        pytest.param(
            {
                "type": "single",
                "data": {
                    "high": [105, 106, 110],
                    "low": [95, 96, 85],
                    "close": [103, 104, 100]
                }
            },
            float('nan'),
            [],
            """
            Pattern: Unclear Trend
            HIGH > prev HIGH: ✅ (110 > 106)
            LOW < prev LOW: ✅ (85 < 96)
            CLOSE > prev HIGH: ❌ (100 <= 106)
            CLOSE < prev LOW: ❌ (100 >= 96)
            """,
            id="single_unclear_trend"
        ),

        # Series Tests
        pytest.param(
            {
                "type": "series",
                "data": {
                    "high": [105, 107, 109, 111],
                    "low": [95, 97, 99, 101],
                    "close": [103, 105, 107, 110]
                }
            },
            10.0,
            ["2024-01-04 00:00:00"],
            """
            Pattern: Valid Uptrend Series
            Bar 1: HIGH=105, LOW=95, CLOSE=103
            Bar 2: HIGH > prev HIGH: ✅ (107 > 105), LOW > prev LOW: ✅ (97 > 95), CLOSE > prev HIGH: ✅ (105 > 105)
            Bar 3: HIGH > prev HIGH: ✅ (109 > 107), LOW > prev LOW: ✅ (99 > 97), CLOSE > prev HIGH: ✅ (107 > 107)
            Bar 4: HIGH > prev HIGH: ✅ (111 > 109), LOW > prev LOW: ✅ (101 > 99), CLOSE > prev HIGH: ✅ (110 > 109)
            """,
            id="series_uptrend"
        ),
        pytest.param(
            {
                "type": "series",
                "data": {
                    "high": [111, 109, 107, 105],
                    "low": [101, 99, 97, 95],
                    "close": [110, 108, 106, 94]
                }
            },
            10.0,
            ["2024-01-04 00:00:00"],
            """
            Pattern: Valid Downtrend Series
            Bar 1: HIGH=111, LOW=101, CLOSE=110
            Bar 2: HIGH < prev HIGH: ✅ (109 < 111), LOW < prev LOW: ✅ (99 < 101), CLOSE < prev LOW: ✅ (108 < 101)
            Bar 3: HIGH < prev HIGH: ✅ (107 < 109), LOW < prev LOW: ✅ (97 < 99), CLOSE < prev LOW: ✅ (106 < 99)
            Bar 4: HIGH < prev HIGH: ✅ (105 < 107), LOW < prev LOW: ✅ (95 < 97), CLOSE < prev LOW: ✅ (94 < 97)
            """,
            id="series_downtrend"
        ),
        pytest.param(
            {
                "type": "series",
                "data": {
                    "high": [105, 107, 109, 106],
                    "low": [95, 97, 99, 101],
                    "close": [103, 105, 107, 105]
                }
            },
            float('nan'),
            [],
            """
            Pattern: Broken Series
            Bar 1: HIGH=105, LOW=95, CLOSE=103
            Bar 2: HIGH > prev HIGH: ✅ (107 > 105), LOW > prev LOW: ✅ (97 > 95), CLOSE > prev HIGH: ✅ (105 > 105)
            Bar 3: HIGH > prev HIGH: ✅ (109 > 107), LOW > prev LOW: ✅ (99 > 97), CLOSE > prev HIGH: ✅ (107 > 107)
            Bar 4: HIGH > prev HIGH: ❌ (106 <= 109), LOW > prev LOW: ✅ (101 > 99), CLOSE > prev HIGH: ❌ (105 <= 109)
            """,
            id="series_broken"
        ),
    ]
)
def test_identify_wide_range_bar_all_scenarios(
    test_data: dict,
    expected_range: float,
    expected_indices: list,
    description: str
):
    """Test identify_wide_range_bar with comprehensive parameterized cases.

    One stop shop for all scenarios. Specific test cases are additioanlly tested individually in the module. 
    
    Args:
        test_data: Dictionary containing test data type and price data
        expected_range: Expected range value (float or nan)
        expected_indices: Expected list of indices
        description: Test case description with pattern conditions
    """
    # Create test data
    if test_data["type"] == "single":
        indices = pd.date_range('2024-01-01', periods=3)
        price_data = pd.DataFrame({
            PriceLabel.OPEN: [100, 101, 100],
            PriceLabel.HIGH: test_data["data"]["high"],
            PriceLabel.LOW: test_data["data"]["low"],
            PriceLabel.CLOSE: test_data["data"]["close"],
        }, index=indices)
        test_idx = indices[2]
    else:  # series
        indices = pd.date_range('2024-01-01', periods=len(test_data["data"]["high"]))
        price_data = pd.DataFrame({
            PriceLabel.OPEN: [100] * len(indices),
            PriceLabel.HIGH: test_data["data"]["high"],
            PriceLabel.LOW: test_data["data"]["low"],
            PriceLabel.CLOSE: test_data["data"]["close"],
        }, index=indices)
        test_idx = indices[-1]

    # Test the target bar
    range_size, wrb_indices = identify_wide_range_bar(price_data, test_idx)
    
    # Convert indices to strings for comparison
    wrb_indices_str = [str(idx) for idx in wrb_indices]
    
    # Assertions
    if pd.isna(expected_range):
        assert pd.isna(range_size), f"Failed for {description}: expected nan range"
    else:
        assert range_size == expected_range, f"Failed for {description}: expected range {expected_range}, got {range_size}"
    
    assert wrb_indices_str == expected_indices, f"Failed for {description}: expected indices {expected_indices}, got {wrb_indices_str}"


# endregion 