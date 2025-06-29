"""Tests for price feed loader and container."""

from pathlib import Path

import pytest
import yaml
from dependency_injector.errors import Error as DIError

from core.feed.container import PriceFeedsContainer
from core.feed.providers.csv_file import CSVPriceFeedProvider
from loaders.generic import load_yaml_config

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_providers_dir(tmp_path):
    """Create a temporary providers directory with test YAML files."""
    providers_dir = tmp_path / "providers"
    providers_dir.mkdir()
    
    # Create CSV provider config with nested structure
    csv_config = {
        "name": "csv",
        "data_dir": "tests/data",
        "file_pattern": "*.csv",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "timeframes": {
            "supported_timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
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
    
    with open(providers_dir / "csv.yaml", "w") as f:
        yaml.dump(csv_config, f)
    
    return providers_dir


@pytest.fixture
def price_feeds_container(temp_providers_dir):
    """Create a price feeds container for testing."""
    container = PriceFeedsContainer()
    container.providers_dir.override(temp_providers_dir)
    return container

# =============================================================================
# CONTAINER INITIALIZATION TESTS
# =============================================================================


def test_price_feeds_container_initialization(price_feeds_container, temp_providers_dir):
    """Test price feeds container initialization."""
    assert price_feeds_container is not None
    assert price_feeds_container.providers_dir() == temp_providers_dir

# =============================================================================
# PROVIDER LOADING TESTS
# =============================================================================


def test_price_feeds_container_all_providers(price_feeds_container):
    """Test loading all providers through container."""
    providers = price_feeds_container.all_providers()
    
    assert len(providers) == 1
    assert "csv" in providers
    
    # Verify providers follow the duck typing contract
    for provider in providers.values():
        required_methods = ['get_price_data']
        for method_name in required_methods:
            assert hasattr(provider, method_name), f"Provider missing method: {method_name}"
            assert callable(getattr(provider, method_name)), f"Provider method not callable: {method_name}"


def test_price_feeds_container_available_providers(price_feeds_container):
    """Test getting available provider names through container."""
    available = price_feeds_container.available_providers()
    assert available == ["csv"]


def test_price_feeds_container_provider_factory(price_feeds_container):
    """Test loading specific provider through container factory."""
    provider = price_feeds_container.provider(name="csv")
    
    assert provider is not None
    assert isinstance(provider, CSVPriceFeedProvider)


def test_price_feeds_container_unknown_provider(price_feeds_container):
    """Test loading unknown provider through container factory."""
    with pytest.raises(ValueError, match="Unknown provider"):
        price_feeds_container.provider(name="unknown")

# =============================================================================
# CONTAINER WIRING TESTS
# =============================================================================


def test_price_feeds_container_wire_success(price_feeds_container):
    """Test successful container wiring."""
    price_feeds_container.wire()


def test_price_feeds_container_wire_missing_providers_dir():
    """Test container wiring with missing providers directory uses default."""
    container = PriceFeedsContainer()
    
    container.wire()
    
    default_path = Path("configs/providers")
    assert container.providers_dir() == default_path


def test_price_feeds_container_wire_invalid_providers_dir_type():
    """Test container wiring with invalid providers directory type."""
    container = PriceFeedsContainer()
    container.providers_dir.override(12345)
    
    with pytest.raises(DIError, match="12345 is not an instance of <class 'pathlib.Path'>"):
        container.providers_dir()


@pytest.mark.xfail(reason="wire() is not getting called by the DI container")
def test_price_feeds_container_wire_nonexistent_providers_dir(tmp_path):
    """Test container wiring with non-existent providers directory."""
    container = PriceFeedsContainer()
    nonexistent_dir = tmp_path / "nonexistent"
    container.providers_dir.override(nonexistent_dir)
    
    print(f"DEBUG: nonexistent_dir = {nonexistent_dir}")
    print(f"DEBUG: nonexistent_dir exists = {nonexistent_dir.exists()}")

    with pytest.raises(ValueError, match="Providers directory does not exist"):
        container.wire()

# =============================================================================
# YAML VALIDATION TESTS
# =============================================================================


def test_integration_yaml_validation(temp_providers_dir):
    """Test YAML config validation with real provider classes."""
    from core.feed.providers.csv_file import CSVPriceFeedConfig

    csv_config = load_yaml_config(temp_providers_dir / "csv.yaml", CSVPriceFeedConfig)
    assert isinstance(csv_config, CSVPriceFeedConfig)
    assert csv_config.name == "csv"

# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


def test_container_handles_yaml_errors(temp_providers_dir):
    """Test that container handles YAML parsing errors gracefully."""
    # Create invalid YAML file
    with open(temp_providers_dir / "invalid.yaml", "w") as f:
        f.write("invalid: yaml: content: [")
    
    container = PriceFeedsContainer()
    container.providers_dir.override(temp_providers_dir)
    
    providers = container.all_providers()
    
    assert "csv" in providers
    assert "invalid" not in providers


def test_container_handles_validation_errors(temp_providers_dir):
    """Test that container handles validation errors gracefully."""
    # Create config with invalid data
    invalid_config = {
        "name": "invalid",
        "invalid_field": "invalid_value"
    }
    
    with open(temp_providers_dir / "invalid.yaml", "w") as f:
        yaml.dump(invalid_config, f)
    
    container = PriceFeedsContainer()
    container.providers_dir.override(temp_providers_dir)
    
    providers = container.all_providers()
    
    assert "csv" in providers
    assert "invalid" not in providers