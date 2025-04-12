
import pandas as pd
import pytest

from main import Direction, PriceLabel, get_trend, is_extreme_bar


def test_100_bar_frame():...


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


# @pytest.mark.skip()
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


# endregion

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

## endregion


# region: first pullback
def test_min_pullback_bars():...

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

