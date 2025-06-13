"""Tests for the root container."""


import pytest
import yaml

from src.core.container.root import RootContainer


@pytest.fixture
def mock_registry_file(tmp_path):
    """Create a mock registry file."""
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
    """Create a temporary directory with mock strategy configs."""
    strategies_dir = tmp_path / "strategies"
    strategies_dir.mkdir()
    # Write a valid strategy YAML file
    strategy = {
        "name": "test_strategy",
        "steps": [
            {"system_step_id": "mock_step", "static_config": {}, "dynamic_config": {}}
        ]
    }
    with open(strategies_dir / "test_strategy.yaml", "w") as f:
        yaml.safe_dump(strategy, f)
    return strategies_dir


def test_root_container_creation(mock_registry_file, temp_strategies_dir):
    """Test creating a root container."""
    # Create container with required dependencies
    container = RootContainer()
    
    # Configure container
    container.config.step_registry.registry_file.from_value(mock_registry_file)
    container.config.strategies.dir.from_value(temp_strategies_dir)
    
    # Wire container
    container.wire()
    
    # Verify containers are created
    assert container.steps.registry() is not None
    assert container.strategies.strategies() is not None 