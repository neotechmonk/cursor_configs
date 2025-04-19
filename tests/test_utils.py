from typing import Optional

import pandas as pd
import pytest

from models import Direction, PriceLabel
from utils import (
    get_trend,
    is_bars_since_extreme_pivot_valid,
    is_extreme_bar,
    is_last_bar_within_bars_count,
    is_within_fib_extension,
)


@pytest.mark.skip("Non implemented")
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


@pytest.mark.skip("Non implemented")
def test_pullback_max_70_pct():...

@pytest.mark.skip("Non implemented")
def test_pullback_min_20_pct():...
# endregion

@pytest.mark.skip("Non implemented")
def test_new_impulse_extension_close_max_1_875():...


@pytest.mark.skip("Non implemented")
def test_new_impulse_extension_close_min_1_875():...

# endregion


# region: Bars to form the pullback + new impulse swing
"""
we dont want to get jacked up or play in larger pattern blocking the funds
"""


@pytest.mark.skip("Non implemented")
def test_pullback_and_new_impulse_min_bars():...

@pytest.mark.skip("Non implemented")
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
        "ref_swing_start_idx": pullback_start_idx,
        "ref_swing_end_idx": pullback_end_idx,
    }

    # Add optional params only if explicitly given
    if min_ext is not None:
        kwargs["min_fib_extension"] = min_ext
    if max_ext is not None:
        kwargs["max_fib_extension"] = max_ext

    result = is_within_fib_extension(**kwargs)
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
        "ref_swing_start_idx": pullback_start_idx,
        "ref_swing_end_idx": pullback_end_idx,
    }

    if min_ext is not None:
        kwargs["min_fib_extension"] = min_ext
    if max_ext is not None:
        kwargs["max_fib_extension"] = max_ext

    result = is_within_fib_extension(**kwargs)
    assert result == expected


# ❌ Invalid trend
def test_guard_invalid_trend_raises_value_error(uptrending_price_feed):
    start_idx = uptrending_price_feed.index[1]
    end_idx = uptrending_price_feed.index[2]

    with pytest.raises(ValueError, match="Unsupported trend"):
        is_within_fib_extension(
            price_feed=uptrending_price_feed,
            trend=Direction.RANGE,  # Invalid trend
            ref_swing_start_idx=start_idx,
            ref_swing_end_idx=end_idx
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
        is_within_fib_extension(
            price_feed=uptrending_price_feed,
            trend=Direction.UP,
            ref_swing_start_idx=start_idx,
            ref_swing_end_idx=end_idx,
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
        is_within_fib_extension(
            price_feed=uptrending_price_feed,
            trend=Direction.UP,
            ref_swing_start_idx=start_idx,
            ref_swing_end_idx=end_idx
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

    # Choose any start and end index (they're both flat)
    start_idx = price_feed.index[1]
    end_idx = price_feed.index[2]

    with pytest.raises(ValueError, match="zero distance"):
        is_within_fib_extension(
            price_feed=price_feed,
            trend=Direction.UP,
            ref_swing_start_idx=start_idx,
            ref_swing_end_idx=end_idx
        )


# endregion 

# region : swing size - reaction to entry
@pytest.mark.parametrize(
    "ref_idx, searched_idx, min_bars, max_bars, expected",
    [
        (0, 4, 4, 4, True),     # Exactly 4 bars between 0 and 4
        (1, 3, 1, 3, True),     # 2 bars between index 1 and 3
        (2, 4, 1, 2, True),     # 2 bars between 2 and 4
        (1, 4, 3, 3, True),     # 3 bars between 1 and 4
        (3, 4, 1, 1, True),     # 1 bar between 3 and 4
        (0, 4, 1, 3, False),    # 4 bars not within range
        (2, 3, 2, 3, False),    # Only 1 bar between 2 and 3
    ]
)
def test_is_last_bar_within_bars_count(
    uptrending_price_feed,
    ref_idx,
    searched_idx,
    min_bars,
    max_bars,
    expected
):
    df = uptrending_price_feed
    ref_bar = df.index[ref_idx]
    searched_bar = df.index[searched_idx]

    result = is_last_bar_within_bars_count(
        price_feed=df,
        ref_bar_idx=ref_bar,
        searched_bar_idx=searched_bar,
        min_bars=min_bars,
        max_bars=max_bars
    )

    assert result is expected


def test_is_last_bar_within_bars_count_guard_invalid_min_max_types(uptrending_price_feed):
    df = uptrending_price_feed
    ref_bar = df.index[0]
    searched_bar = df.index[1]

    with pytest.raises(TypeError, match="min_bars and max_bars must be integers"):
        is_last_bar_within_bars_count(df, ref_bar, searched_bar, min_bars="two", max_bars=5)

    with pytest.raises(TypeError, match="min_bars and max_bars must be integers"):
        is_last_bar_within_bars_count(df, ref_bar, searched_bar, min_bars=1, max_bars=5.0)


def test_is_last_bar_within_bars_count_guard_ref_bar_not_in_index(uptrending_price_feed):
    df = uptrending_price_feed
    fake_ref = pd.Timestamp("1999-01-01")
    searched_bar = df.index[-1]

    with pytest.raises(ValueError, match="Reference index .* not in price feed"):
        is_last_bar_within_bars_count(df, fake_ref, searched_bar, min_bars=1, max_bars=5)


def test_is_last_bar_within_bars_count__guard_searched_bar_not_in_index(uptrending_price_feed):
    df = uptrending_price_feed
    ref_bar = df.index[0]
    fake_searched = pd.Timestamp("2099-01-01")

    with pytest.raises(ValueError, match="Searched index .* not in price feed"):
        is_last_bar_within_bars_count(df, ref_bar, fake_searched, min_bars=1, max_bars=5)


def test_is_last_bar_within_bars_count__guard_searched_bar_precedes_ref_bar(uptrending_price_feed):
    df = uptrending_price_feed
    ref_bar = df.index[3]
    searched_bar = df.index[1]

    with pytest.raises(ValueError, match="Reference index .* should precede searched index .*"):
        is_last_bar_within_bars_count(df, ref_bar, searched_bar, min_bars=1, max_bars=5)

# endregion

# region: Setup
"""
we dont want to get jacked up or play in larger pattern blocking the funds
"""


@pytest.mark.skip("Non implemented")
def test_setup_stop_25_pct():...

@pytest.mark.skip("Non implemented")
def test_setup_entry_25_pct():...


@pytest.mark.skip("Non implemented")
def test_setup_target():
    """target is part of management - agnostic of strategy"""
    pass
# endregion

# region : Process bar for the Strategy




# endregion