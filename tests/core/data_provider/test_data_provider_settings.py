from pathlib import Path

import pandas as pd
import pytest
from pydantic import BaseModel

from core.data_provider.providers.csv import (
    CSVPriceFeedConfig,
    CSVPriceFeedProvider,
    RawCSVPriceFeedConfig,
)
from core.data_provider.settings import DataProviderMetadata, DataProviderSettings


class DummyDataProvider():
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:...


class RawDummyPriceFeedConfig(BaseModel):...


class DummyPriceFeedConfig(BaseModel):...


@pytest.fixture
def mock_provider_settings(monkeypatch):
    # JSON-like raw dict as you'd load from config/settings.json
    raw_json_dict = {
        "config_dir": "/mock/path/to/data",
        "providers": {
            "dummy": {
                "raw_config": f"{RawDummyPriceFeedConfig.__module__}.{RawDummyPriceFeedConfig.__name__}",
                "target_config": f"{DummyPriceFeedConfig.__module__}.{DummyPriceFeedConfig.__name__}",
                "provider_class": f"{DummyDataProvider.__module__}.{DummyDataProvider.__name__}",
                "extra": {
                    "source": "test",
                    "version": "1.0",
                    "note": "used for isolated unit tests"
                }
            }
        }
    }
    return raw_json_dict


def test_default_data_provider_settings():
    settings = DataProviderSettings()

    # Check default config_dir
    assert settings.config_dir == Path("configs/providers/data")

    # Check providers dict exists and contains 'csv'
    assert settings.providers == {}



def test_provider_resolution(mock_provider_settings):
    settings = DataProviderSettings(**mock_provider_settings)
    dummy_metadata = settings.providers["dummy"]
    
    assert dummy_metadata.raw_config is RawDummyPriceFeedConfig
    assert dummy_metadata.target_config is DummyPriceFeedConfig
    assert dummy_metadata.provider_class is DummyDataProvider
    assert dummy_metadata.extra["note"] == "used for isolated unit tests"

    #Test overridden default provider
    with pytest.raises(KeyError):
        settings.providers["csv"]
    