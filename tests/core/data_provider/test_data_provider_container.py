from pathlib import Path

import pandas as pd
import pytest
from pydantic import BaseModel

from core.data_provider.container import DataProviderContainer
from core.data_provider.service import DataProviderService
from core.data_provider.settings import DataProviderMetadata, DataProviderSettings


class DummyDataProvider():
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:...


class RawDummyPriceFeedConfig(BaseModel):...


class DummyPriceFeedConfig(BaseModel):...


@pytest.fixture
def mock_provider_settings():
    return DataProviderSettings(
        config_dir=Path("/mock/path/to/data"),
        providers={
            "dummy": DataProviderMetadata(
                raw_config=RawDummyPriceFeedConfig,
                target_config=DummyPriceFeedConfig,
                provider_class=DummyDataProvider
            )
        }
    )


@pytest.fixture
def mock_data_provider_container(mock_provider_settings):
    container = DataProviderContainer()
    container.settings.override(mock_provider_settings)
    # container.wire()
    yield container
    container.unwire()


def test_data_provider_container_resolves_service(mock_data_provider_container):
    service: DataProviderService = mock_data_provider_container.service()

    assert isinstance(service, DataProviderService)

    # print(service.registry)
    assert service.config_dir == Path("/mock/path/to/data")
    assert "dummy" in service.registry
    assert service.registry["dummy"].provider_class is DummyDataProvider