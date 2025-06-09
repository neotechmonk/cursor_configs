
import pytest
import yaml

from core.container.strategies import StrategiesContainer
from src.models.system import StrategyStepRegistry, StrategyStepTemplate


@pytest.fixture
def mock_step_registry():
    # Minimal mock registry with one template
    template = StrategyStepTemplate(
        system_step_id="mock_step",
        function="mock.func",
        input_params_map={},
        return_map={},
        config_mapping={}
    )
    return StrategyStepRegistry(steps={"mock_step": template})


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


def test_strategy_container_wiring(mock_step_registry, temp_strategies_dir):
    container = StrategiesContainer(
        config={"strategies_dir": temp_strategies_dir},
        step_registry=mock_step_registry
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