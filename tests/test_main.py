

import pandas as pd
import pytest

from main import Direction, PriceLabel, detect_direction


@pytest.fixture
def uptrending_price_feed():
    dates = pd.date_range(start="2023-01-01", periods=5, freq="B")  # 5 business days
    return pd.DataFrame({
        PriceLabel.OPEN:  [95, 96, 97, 98, 99],
        PriceLabel.HIGH:  [95, 96, 97, 98, 100],
        PriceLabel.LOW:   [70, 81, 82, 83, 81],
        PriceLabel.CLOSE: [70, 81, 82, 83, 84]
    }, index=dates)


@pytest.fixture
def downtrending_price_feed():
    dates = pd.date_range(start="2023-01-01", periods=5, freq="B")  # 5 business days
    return pd.DataFrame({
        PriceLabel.OPEN:  [105, 104, 103, 102, 101],
        PriceLabel.HIGH:  [106, 105, 104, 103, 102],
        PriceLabel.LOW:   [95, 94, 93, 92, 91],
        PriceLabel.CLOSE: [96, 95, 94, 93, 92]
    }, index=dates)


# Fix : unrealistic data - identical highs and lows
@pytest.fixture
def rangebound_price_feed():
    dates = pd.date_range(start="2023-01-01", periods=5, freq="B")  # 5 business days
    return pd.DataFrame({
        PriceLabel.OPEN:  [100, 101, 100, 99, 100],
        PriceLabel.HIGH:  [105, 105, 105, 105, 105],
        PriceLabel.LOW:   [90,  90,  90,  90,  90],
        PriceLabel.CLOSE: [100, 100, 101, 100, 99]
    }, index=dates)


def test_100_bar_frame():...

def test_100_bar_high_or_low():...


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
    result = detect_direction(price_feed)
    assert result == expected_direction


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

