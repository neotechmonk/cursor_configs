from pathlib import Path

import pytest
import yaml
from pydantic import BaseModel

from core.data_provider.protocol import DataProviderProtocol
from core.data_provider.provider import DataProviderService
from core.data_provider.settings import DataProviderMetadata
from util.custom_cache import ScopedCacheView, WatchedCache


# --- Dummy classes for test ---
class DummyRawConfig(BaseModel):
    name: str
    foo: str = "bar"


class DummyTargetConfig(BaseModel):
    name: str
    foo: str


class DummyProvider(DataProviderProtocol):
    def __init__(self, config: DummyTargetConfig):
        self.config = config

    def get_price_data(self, symbol: str, timeframe: str):
        return f"Price data for {symbol} at {timeframe}"


# --- Fixture: write dummy config ---
@pytest.fixture
def dummy_config_file(tmp_path: Path):
    config = {
        "name": "dummy",
        "foo": "bar"
    }
    path = tmp_path / "dummy.yaml"
    with path.open("w") as f:
        yaml.dump(config, f)
    return path


# --- Happy path test ---
def test_load_data_provider_by_name_happy_path(dummy_config_file):
    cache = ScopedCacheView(cache=WatchedCache(), namespace="test_ns")
    service = DataProviderService(config_dir=dummy_config_file.parent, cache=cache)

    service.registry = {
        "dummy": DataProviderMetadata(
            raw_config=DummyRawConfig,
            target_config=DummyTargetConfig,
            provider_class=DummyProvider
        )
    }

    provider = service.get("dummy")

    assert isinstance(provider, DummyProvider)
    assert provider.config.name == "dummy"
    assert provider.config.foo == "bar"
    assert isinstance(provider.get_price_data("BTC", "1h"), str)