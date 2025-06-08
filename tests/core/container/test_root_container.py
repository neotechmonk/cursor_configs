"""Tests for the root container."""

from pathlib import Path

import pytest
import yaml

from src.core.container.root import RootContainer
from src.models.system import StrategyStepRegistry


@pytest.fixture
def temp_registry_file(tmp_path):
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


def test_root_container_integration(temp_registry_file, temp_strategies_dir):
    """Test that the root container properly wires up the step registry and strategy containers."""
    container = RootContainer()
    container.config.step_registry.registry_file.from_value(temp_registry_file)
    container.config.strategy.strategies_dir.from_value(temp_strategies_dir)
    container.wire()
    
    # Test that the step registry is properly injected into the strategy container
    strategy = container.strategy.strategy("test_strategy")
    assert strategy.steps[0].template.system_step_id == "mock_step"
    
    # Test that the strategy container can access the step registry's templates
    assert strategy.steps[0].template.function == "mock.func" 