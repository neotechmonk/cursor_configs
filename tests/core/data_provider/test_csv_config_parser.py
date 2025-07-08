import pytest

from core.data_provider.csv import (
    CSVPriceFeedConfig,
    RawCSVPriceFeedConfig,
    resolve_csv_pricefeed_config,
)


@pytest.fixture
def raw_csv_pricefeed_model() -> RawCSVPriceFeedConfig:
    return RawCSVPriceFeedConfig(
        name="csv",
        data_dir="tests/data",
        file_pattern="*.csv",
        date_format="%Y-%m-%d %H:%M:%S",
        timeframes={
            "supported_timeframes": ["1m", "5m", "1d"],
            "native_timeframe": "1m",
            "resample_strategy": {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }
        }
    )


def test_resolve_csv_pricefeed_config(raw_csv_pricefeed_model):
    resolved: CSVPriceFeedConfig = resolve_csv_pricefeed_config(raw_csv_pricefeed_model)

    assert resolved.name == "csv"
    assert resolved.data_dir == "tests/data"
    assert resolved.file_pattern == "*.csv"
    assert str(resolved.timeframes.native_timeframe) == "1m"
    assert resolved.timeframes.resample_strategy.volume == "sum"