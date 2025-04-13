
from typing import Optional

import pandas as pd
import pytest

from main import (
    Direction,
    PriceLabel,
    get_trend,
    is_bars_since_extreme_pivot_valid,
    is_extreme_bar,
    is_new_impulse_extension_valid,
)


def test_100_bar_frame():...

# region: Detect Direction
@pytest.mark.parametrize(
    "price_feed_fixture, expected_direction",
    [
        ("uptrending_price_feed", Direction.UP),
        ("downtrending_price_feed", Direction.DOWN),
        ("rangebound_price_feed", Direction.RANGE),
        
    ]
)
def test_direction(price_feed_fixture, expected_direction, request):
    price_feed = request.getfixturevalue(price_feed_fixture)
    result = get_trend(price_feed)
    assert result == expected_direction

# endregion


# region: latest bar is a frame extreme 
@pytest.mark.parametrize(
    "price_feed_fixture, direction, frame_size,  expected_result",
    [
        ("uptrending_price_feed", Direction.UP, None, True), # defaults to len(feed)
        ("uptrending_price_feed", Direction.UP, 5, True), # == len(feed)
        ("uptrending_price_feed", Direction.UP, 4, True), #  len(feed) - 1
        ("downtrending_price_feed", Direction.DOWN, None, True),# defaults to len(feed)
        ("downtrending_price_feed", Direction.DOWN, 5, True),# == len(feed)
        ("downtrending_price_feed", Direction.DOWN, 3, True),  #  len(feed) - 2
        
    ]
)
def test_is_extreme_bar_true(price_feed_fixture, direction, frame_size, expected_result, request):
    price_feed = request.getfixturevalue(price_feed_fixture)
    result = is_extreme_bar(price_feed=price_feed,trend=direction, frame_size=frame_size)
    assert result == expected_result


@pytest.mark.parametrize(
    "price_feed_fixture, direction, frame_size",
    [
        ("uptrending_price_feed", Direction.UP, None),
        ("uptrending_price_feed", Direction.UP, 5),
        ("uptrending_price_feed", Direction.UP, 4),
        ("downtrending_price_feed", Direction.DOWN, None),
        ("downtrending_price_feed", Direction.DOWN, 5),
        ("downtrending_price_feed", Direction.DOWN, 3)
    ]
)
def test_is_extreme_bar_false(price_feed_fixture, direction, frame_size, request):
    price_feed = request.getfixturevalue(price_feed_fixture)

    future_index = pd.to_datetime("2262-04-11")  # Max safe datetime in pandas

    if direction == Direction.UP:
        # Add a bar with a HIGH equal to or below history → not an extreme
        new_bar = pd.DataFrame([{
            PriceLabel.OPEN.value: 0,
            PriceLabel.HIGH.value: 0,  # Not a new high
            PriceLabel.LOW.value: 0,
            PriceLabel.CLOSE.value: 0
        }], index=[future_index])

    elif direction == Direction.DOWN:
        # Add a bar with a LOW equal to or above history → not a new low
        new_bar = pd.DataFrame([{
            PriceLabel.OPEN.value: 0,
            PriceLabel.HIGH.value: 0,
            PriceLabel.LOW.value: 1_000_000_000,  # Not a new low
            PriceLabel.CLOSE.value: 0
        }], index=[future_index])

    price_feed = pd.concat([price_feed, new_bar])

    result = is_extreme_bar(price_feed=price_feed, trend=direction, frame_size=frame_size)
    assert not result

    
def test_is_extreme_invalid_trend(uptrending_price_feed):
    with pytest.raises(ValueError, match="Market must trend UP or DOWN"):
        is_extreme_bar(uptrending_price_feed, trend=Direction.RANGE)


def test_is_extreme_larger_frame_size_raises(uptrending_price_feed):
    with pytest.raises(ValueError, match="Frame size is larger the bars in the `price_feed`"):
        is_extreme_bar(uptrending_price_feed, trend=Direction.UP, frame_size=1000)


@pytest.mark.parametrize(
    "price_feed_fixture, direction, frame_size",
    [
        ("uptrending_price_feed", Direction.UP, 0),
        ("uptrending_price_feed", Direction.UP, -1),
        ("downtrending_price_feed", Direction.DOWN, 0),
        ("downtrending_price_feed", Direction.DOWN, -3 ),
    ]

)
def test_is_extreme_invalid_frame_size_raises(price_feed_fixture, direction, frame_size, request):
    price_feed = request.getfixturevalue(price_feed_fixture)
    with pytest.raises(ValueError, match="Frame size must be at least 1"):
        is_extreme_bar(price_feed, trend=direction, frame_size=frame_size)


#endregion


# region: first pullback


@pytest.mark.parametrize(
    "frame_extreme_pos, min_bars, max_bars, expected_result",         #frame_extreme_pos in zero inx pos. E.g 999 is the last of df with len 1000
    [
        (990, 5, 10, True),   # 1000 - 990 - 1 = 9 bars since swing → in range
        (990, 5, None, True),   # max_bars = len(df)
        (995, 5, 10, False),   # 4 bars since extremene. max ✅  & min ❌
        (990, 5, 8, False),   # 9 bars since extremene. max ❌  & min ✅
        (999, 5, 10, False),  # 0 bars since swing → not enough
    ]
)
def test_is_bars_since_extreme_pivot_valid(
    frame_extreme_pos: int,
    min_bars: Optional[int],
    max_bars: Optional[int],
    expected_result: bool
):
    bars = 1000
    dates = pd.date_range(start="2023-01-01", periods=bars, freq="D")
    synth_prices_df = pd.DataFrame({"high": range(bars)}, index=dates)

    # Convert position to actual index label
    frame_extreme_idx = synth_prices_df.index[frame_extreme_pos]
    print(frame_extreme_idx)

    result = is_bars_since_extreme_pivot_valid(synth_prices_df, frame_extreme_idx, min_bars, max_bars)
    assert result == expected_result


def test_pullback_max_70_pct():...

def test_pullback_min_20_pct():...
# endregion

def test_new_impulse_extension_close_max_1_875():...


def test_new_impulse_extension_close_min_1_875():...

# endregion


# region: Bars to form the pullback + new impulse swing
"""
we dont want to get jacked up or play in larger pattern blocking the funds
"""


def test_pullback_and_new_impulse_min_bars():...
def test_pullback_and_new_impulse_max_bars():...
# endregion

# region : New Impulse : fib extension range 

@pytest.mark.parametrize(
    "pullback_start_pos, pullback_end_pos, min_ext, max_ext, expected",
    [
        (1, 2, None, None, False),       # uses default min=1.35, max=1.875 → fib=2.0 → ❌
        (1, 2, None, 2.0, True),         # uses default; fib_ext = 2.0, at upper bound, above min → ✅
        (1, 2, 1, None, False),         # uses default; fib_ext = 2.0, under upper bound, above min → ❌
        (1, 2, 1.0, 2.0, True),         # fib_ext = 2.0, at upper bound
        (1, 2, 1.5, 2.0, True),         # fib_extb = 2.0, within range
        (1, 2, 1.7, 1.9, False),        # fib_ext = 2.0, exceeds max
        (1, 2, 2.1, 3, False),        # fib_ext = 2.0, doesnt meet mina
    ]
)
def test_is_new_impulse_extension_up_trend(
    pullback_start_pos,
    pullback_end_pos,
    min_ext,
    max_ext,
    expected, uptrending_price_feed
    ):
    # Setup: synthetic prices
    dates = pd.date_range("2023-01-01", periods=5, freq="D")

    # Price structure designed to create fib extension of 2.0:
    # Pullback high = 106, pullback low = 92 → pullback = 14
    # Current high = 120 → impulse = 28 → fib = 28 / 14 = 2.0

    data = {
        PriceLabel.OPEN:  [100, 95, 98, 110, 115],
        PriceLabel.HIGH:  [101, 106,  99, 111, 120],  # current high is last bar
        PriceLabel.LOW:   [94,  91,  92, 108, 109],
        PriceLabel.CLOSE: [100, 93,  95, 110, 117],
    }

    price_feed = pd.DataFrame(data, index=dates)
    pullback_start_idx = dates[pullback_start_pos]
    pullback_end_idx = dates[pullback_end_pos]

    kwargs = {
        "price_feed": price_feed,
        "trend": Direction.UP,
        "pullback_start_idx": pullback_start_idx,
        "pullback_end_idx": pullback_end_idx,
    }

    # Add optional params only if explicitly given
    if min_ext is not None:
        kwargs["min_fib_extension"] = min_ext
    if max_ext is not None:
        kwargs["max_fib_extension"] = max_ext

    result = is_new_impulse_extension_valid(**kwargs)
    assert result == expected


@pytest.mark.parametrize(
    "pullback_start_pos, pullback_end_pos, min_ext, max_ext, expected",
    [
        (1, 2, None, None, False),       # uses default min=1.35, max=1.875 → fib=2.0 → ❌
        (1, 2, None, 2.0, True),         # default min, custom max → fib = 2.0 → ✅
        (1, 2, 1.0, None, False),        # custom min, default max → fib = 2.0 → ❌
        (1, 2, 1.0, 2.0, True),          # fib = 2.0, upper bound → ✅
        (1, 2, 1.5, 2.0, True),          # fib = 2.0, within range → ✅
        (1, 2, 1.7, 1.9, False),         # fib = 2.0, exceeds max → ❌
        (1, 2, 2.1, 3.0, False),         # fib = 2.0, below min → ❌
    ]
)
def test_is_new_impulse_extension_down_trend(
    pullback_start_pos,
    pullback_end_pos,
    min_ext,
    max_ext,
    expected
):
    dates = pd.date_range("2023-01-01", periods=5, freq="D")

    # DOWN trend structure:
    # Pullback low = 91 at pos 1, high = 125 at pos 2 → pullback = 34
    # Current low = 57 at pos 4 → impulse = 125 - 57 = 68 → fib = 68 / 34 = 2.0
  
    data = {
        PriceLabel.OPEN:  [130, 120, 110, 105, 95],
        PriceLabel.HIGH:  [132, 123, 125, 108, 105],  # pullback high = 125
        PriceLabel.LOW:   [100, 91,  105, 89, 57],    # pullback low = 91, current low = 57
        PriceLabel.CLOSE: [129, 93,  110, 91, 60],
    }
    price_feed = pd.DataFrame(data, index=dates)

    pullback_start_idx = dates[pullback_start_pos]
    pullback_end_idx = dates[pullback_end_pos]

    kwargs = {
        "price_feed": price_feed,
        "trend": Direction.DOWN,
        "pullback_start_idx": pullback_start_idx,
        "pullback_end_idx": pullback_end_idx,
    }

    if min_ext is not None:
        kwargs["min_fib_extension"] = min_ext
    if max_ext is not None:
        kwargs["max_fib_extension"] = max_ext

    result = is_new_impulse_extension_valid(**kwargs)
    assert result == expected


# ❌ Invalid trend
def test_guard_invalid_trend_raises_value_error(uptrending_price_feed):
    start_idx = uptrending_price_feed.index[1]
    end_idx = uptrending_price_feed.index[2]

    with pytest.raises(ValueError, match="Unsupported trend"):
        is_new_impulse_extension_valid(
            price_feed=uptrending_price_feed,
            trend=Direction.RANGE,  # Invalid trend
            pullback_start_idx=start_idx,
            pullback_end_idx=end_idx
        )


# ❌ Invalid min/max types
@pytest.mark.parametrize("min_ext, max_ext", [
    (None, 1.8),
    (1.3, None),
    ("low", 1.8),
    (1.3, "high"),
])
def test_guard_invalid_min_max_types_raises_type_error(uptrending_price_feed, min_ext, max_ext):
    start_idx = uptrending_price_feed.index[1]
    end_idx = uptrending_price_feed.index[2]

    with pytest.raises(TypeError, match="min_fib_extension and max_fib_extension must be numeric"):
        is_new_impulse_extension_valid(
            price_feed=uptrending_price_feed,
            trend=Direction.UP,
            pullback_start_idx=start_idx,
            pullback_end_idx=end_idx,
            min_fib_extension=min_ext,
            max_fib_extension=max_ext
        )


# ❌ Invalid index order (start >= end)
@pytest.mark.parametrize("start_pos, end_pos", [
    (2, 2),  # equal
    (3, 2),  # reversed
    # (3, 5),  # control
])
def test_guard_invalid_index_order_raises_value_error(uptrending_price_feed, start_pos, end_pos):
    start_idx = uptrending_price_feed.index[start_pos]
    end_idx = uptrending_price_feed.index[end_pos]

    with pytest.raises(ValueError, match="start=.*must be before end"):
        is_new_impulse_extension_valid(
            price_feed=uptrending_price_feed,
            trend=Direction.UP,
            pullback_start_idx=start_idx,
            pullback_end_idx=end_idx
        )


# ❌ Zero pullback distance (identical high and low)
def test_guard_zero_pullback_distance_raises_value_error():
    # Create a DataFrame where all highs and lows are equal across the frame
    dates = pd.date_range(start="2023-01-01", periods=5, freq="B")
    price_feed = pd.DataFrame({
        PriceLabel.OPEN:  [100, 100, 100, 100, 100],
        PriceLabel.HIGH:  [105, 90, 90, 105, 105],  # fake high 90 for index 1, 2
        PriceLabel.LOW:   [90,  90,  90,  90,  90],  # fake low 90 for index 1, 2
        PriceLabel.CLOSE: [95,  95,  95,  95,  95]
    }, index=dates)

    # Choose any start and end index (they’re both flat)
    start_idx = price_feed.index[1]
    end_idx = price_feed.index[2]

    with pytest.raises(ValueError, match="zero distance"):
        is_new_impulse_extension_valid(
            price_feed=price_feed,
            trend=Direction.UP,
            pullback_start_idx=start_idx,
            pullback_end_idx=end_idx
        )

# endregion 

# region: Setup
"""
we dont want to get jacked up or play in larger pattern blocking the funds
"""


def test_setup_stop_25_pct():...
def test_setup_entry_25_pct():...


def test_setup_target():
    """target is part of management - agnostic of strategy"""
    pass
# endregion

