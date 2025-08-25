"""Tests for the root container - app integration only."""

import pytest
import yaml
from src.core.container.root import RootContainer


@pytest.fixture
def mock_registry_file(tmp_path):
    """Create a mock registry file for app testing."""
    registry_file = tmp_path / "registry.yaml"
    registry = {
        "steps": {
            "mock_step": {
                "function": "mock.func",
                "input_params_map": {},
                "return_map": {},
                "config_mapping": {}
            }
        }
    }
    with open(registry_file, "w") as f:
        yaml.safe_dump(registry, f)
    return registry_file


@pytest.fixture
def temp_strategies_dir(tmp_path):
    """Create a temporary directory with mock strategy configs for app testing."""
    strategies_dir = tmp_path / "strategies"
    strategies_dir.mkdir()
    
    strategy = {
        "name": "test_strategy",
        "steps": [
            {"system_step_id": "mock_step", "static_config": {}, "dynamic_config": {}}
        ]
    }
    with open(strategies_dir / "test_strategy.yaml", "w") as f:
        yaml.safe_dump(strategy, f)
    return strategies_dir


@pytest.fixture
def temp_providers_dir(tmp_path):
    """Create a temporary providers directory for app testing."""
    providers_dir = tmp_path / "providers"
    providers_dir.mkdir()
    
    # Create a basic CSV provider config
    csv_config = {
        "name": "csv",
        "data_dir": "tests/data",
        "file_pattern": "*.csv",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "timeframes": {
            "supported_timeframes": ["1m", "5m", "15m"],
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
        yaml.safe_dump(csv_config, f)
    
    return providers_dir


def test_app_can_startup(mock_registry_file, temp_strategies_dir, temp_providers_dir):
    """Test that the app can start up with the root container."""
    container = RootContainer()
    
    # Configure with app's requirements
    container.config.step_registry.registry_file.from_value(mock_registry_file)
    container.config.strategies.dir.from_value(temp_strategies_dir)
    container.config.price_feeds.providers_dir.from_value(temp_providers_dir)
    
    # App startup - wire the container
    container.wire()
    
    # App is now ready to use


def test_app_can_access_dependencies(mock_registry_file, temp_strategies_dir, temp_providers_dir):
    """Test that the app can access its required dependencies."""
    container = RootContainer()
    container.config.step_registry.registry_file.from_value(mock_registry_file)
    container.config.strategies.dir.from_value(temp_strategies_dir)
    container.config.price_feeds.providers_dir.from_value(temp_providers_dir)
    container.wire()
    
    # App can access step registry
    step_registry = container.steps.registry()
    assert step_registry is not None
    
    # App can access strategies
    strategies = container.strategies.strategies()
    assert strategies is not None
    
    # App can access price feeds
    price_feeds = container.price_feeds.all_providers()
    assert price_feeds is not None


def test_app_configuration_works(mock_registry_file, temp_strategies_dir, temp_providers_dir):
    """Test that the app's configuration works correctly."""
    container = RootContainer()
    container.config.step_registry.registry_file.from_value(mock_registry_file)
    container.config.strategies.dir.from_value(temp_strategies_dir)
    container.config.price_feeds.providers_dir.from_value(temp_providers_dir)
    container.wire()
    
    # App can load strategies from configured directory
    strategies = container.strategies.strategies()
    assert "test_strategy" in strategies
    
    # App can access step registry from configured file
    step_registry = container.steps.registry()
    assert "mock_step" in step_registry.steps
    
    # App can access price feeds from configured directory
    price_feeds = container.price_feeds.all_providers()
    assert "csv" in price_feeds