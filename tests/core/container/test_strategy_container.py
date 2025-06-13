"""Tests for the strategy container."""


import pytest
import yaml

from src.core.container.strategies import StrategiesContainer
from src.models.system import StrategyStepRegistry, StrategyStepTemplate


@pytest.fixture
def mock_step_registry():
    """Create a mock step registry."""
    return StrategyStepRegistry(steps={
        "mock_step": StrategyStepTemplate(
            system_step_id="mock_step",
            function="mock.func",
            input_params_map={},
            return_map={},
            config_mapping={}
        )
    })


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


def test_strategy_container_creation(mock_step_registry, temp_strategies_dir):
    """Test creating a strategy container."""
    # Create container with required dependencies
    container = StrategiesContainer(
        step_registry=mock_step_registry,
        strategies_dir=temp_strategies_dir
    )
    
    # Wire container
    container.wire()
    
    # Verify strategies are loaded
    assert container.strategies() is not None
    assert len(container.available_strategies()) == 1
    assert "test_strategy" in container.available_strategies()


def test_strategy_container_wiring(mock_step_registry, temp_strategies_dir):
    container = StrategiesContainer(
        step_registry=mock_step_registry,
        strategies_dir=temp_strategies_dir
    )
    container.wire()
    
    # Test strategies
    strategies = container.strategies()
    assert "test_strategy" in strategies
    
    # Test available_strategies
    names = container.available_strategies()
    assert names == ["test_strategy"]
    
    # Test strategy factory
    strat = container.strategy("test_strategy")
    assert strat.name == "test_strategy" 