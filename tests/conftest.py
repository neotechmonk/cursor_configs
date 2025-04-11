import pandas as pd
import pytest

from main import PriceLabel


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
