

from core.data_provider.config import PricefeedTimeframeConfig
from core.data_provider.csv import CSVPriceFeedConfig, resolve_csv_pricefeed_config


def test_resolve_csv_pricefeed_config_from_raw_dict():
    raw = {
        "name": "csv",
        "data_dir": "tests/data",
        "file_pattern": "*.csv",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "timeframes": {
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
    }

    config = resolve_csv_pricefeed_config(raw)

    assert isinstance(config, CSVPriceFeedConfig)
    assert config.name == "csv"
    assert config.data_dir == "tests/data"
    assert config.file_pattern == "*.csv"
    assert config.date_format == "%Y-%m-%d %H:%M:%S"

    assert isinstance(config.timeframes, PricefeedTimeframeConfig)
    assert str(config.timeframes.native_timeframe) == "1m"
    assert sorted(str(tf) for tf in config.timeframes.supported_timeframes) == sorted(["1m", "5m", "1d"])
    assert config.timeframes.resample_strategy.volume == "sum"