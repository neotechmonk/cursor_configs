from dataclasses import dataclass
from pathlib import Path
from typing import Type

import pytest
import yaml
from pydantic import BaseModel

from util.provider_builder import ProviderBuilder

# --- Mock Definitions ---


class MockRawConfig(BaseModel):
    api_key: str
    endpoint: str
    name: str = None  # Set by ProviderBuilder


class MockTargetConfig(BaseModel):
    api_key: str
    endpoint: str
    name: str


@dataclass
class MockProvider:
    config: MockTargetConfig


@dataclass
class MockMetadata:
    raw_config: Type[MockRawConfig]
    target_config: Type[MockTargetConfig]
    provider_class: Type[MockProvider]


# --- Fixtures ---

@pytest.fixture
def temp_config_path(tmp_path: Path) -> Path:
    config = {
        "api_key": "abc123",
        "endpoint": "https://api.example.com"
    }
    config_path = tmp_path / "mock_provider.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return config_path


@pytest.fixture
def mock_metadata() -> MockMetadata:
    return MockMetadata(
        raw_config=MockRawConfig,
        target_config=MockTargetConfig,
        provider_class=MockProvider
    )


# --- Tests ---

def test_provider_builder_load_and_build(temp_config_path, mock_metadata):
    builder = ProviderBuilder(
        config_path=temp_config_path,
        meta_data=mock_metadata
    )

    # Run full lifecycle
    provider = builder.load_config().get_provider().build()

    # Assert output provider is as expected
    assert isinstance(provider, MockProvider)
    assert provider.config.api_key == "abc123"
    assert provider.config.endpoint == "https://api.example.com"
    assert provider.config.name == "mock_provider"