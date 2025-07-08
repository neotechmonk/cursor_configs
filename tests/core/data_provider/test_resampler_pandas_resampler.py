
import pandas as pd
import pytest

from core.data_provider.resampler import pandas_resampler
from core.time import CustomTimeframe


@pytest.fixture
def sample_ohlcv_data():
    """Create 1-minute OHLCV sample data over 5 minutes."""
    return pd.DataFrame({
        "open": [100, 101, 102, 103, 104],
        "high": [101, 102, 103, 104, 105],
        "low": [99, 100, 101, 102, 103],
        "close": [100.5, 101.5, 102.5, 103.5, 104.5],
        "volume": [10, 20, 30, 40, 50],
    }, index=pd.date_range(start="2023-01-01 09:00", periods=5, freq="1min"))


def test_pandas_resampler_happy_path(sample_ohlcv_data):
    from_tf = CustomTimeframe("1m")
    to_tf = CustomTimeframe("5m")

    result = pandas_resampler(sample_ohlcv_data, from_tf, to_tf)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1  # Should collapse 5x1min bars into 1x5min bar

    row = result.iloc[0]
    assert row["open"] == 100
    assert row["high"] == 105
    assert row["low"] == 99
    assert row["close"] == 104.5
    assert row["volume"] == 150

    assert result.index[0] == pd.Timestamp("2023-01-01 09:00:00")