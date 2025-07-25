from unittest.mock import Mock

import pytest

from core.strategy.hydration import hydrate_strategy_config
from core.strategy.model import (
    RawStrategyConfig,
    StrategyConfig,
    StrategyStepDefinition,
    StrategyStepInstance,
)


def mock_check_fib() :
    return True


def mock_validate_pullback() :
    return True

@pytest.fixture
def raw_strategy_dict():
    return {
        "name": "Trend Following Strategy",
        "steps": [
            {
                "id": "check_fib",
                "description": "Check Fibonacci criteria",
                "config_bindings": {},
                "runtime_bindings": {
                    "trend": "trend",
                    "ref_swing_start_idx": "bar_index_start",
                    "ref_swing_end_idx": "bar_index_end"
                },
                "reevaluates": ["validate_pullback"]
            },
            {
                "id": "validate_pullback",
                "description": "Validate pullback after fib",
                "config_bindings": {},
                "runtime_bindings": {},
                "reevaluates": []
            }
        ]
    }


@pytest.fixture
def mock_step_service():
    """Mock StrategyStepService with controlled .get behavior."""
    mock = Mock()
    
    # Mocked step definitions
    check_fib_def = StrategyStepDefinition(
        id="check_fib",
        function_path=f"{mock_check_fib.__module__}.{mock_check_fib.__name__}",
        input_bindings={},
        output_bindings={"result": StrategyStepDefinition.OutputBinding(mapping="_")}
    )

    validate_pullback_def = StrategyStepDefinition(
        id="validate_pullback",
        function_path=f"{mock_validate_pullback.__module__}.{mock_validate_pullback.__name__}",
        input_bindings={},
        output_bindings={"valid": StrategyStepDefinition.OutputBinding(mapping="_")}
    )

    def _get(name):
        if name == "check_fib":
            return check_fib_def
        elif name == "validate_pullback":
            return validate_pullback_def
        else:
            return None

    mock.get.side_effect = _get
    return mock


def test_hydrate_strategy_config_success(raw_strategy_dict, mock_step_service):
    raw_config = RawStrategyConfig(**raw_strategy_dict)
    hydrated = hydrate_strategy_config(raw_config, mock_step_service)

    assert isinstance(hydrated, StrategyConfig)
    assert hydrated.name == "Trend Following Strategy"
    assert len(hydrated.steps) == 2

    check_fib = next(s for s in hydrated.steps if s.step_definition.id == "check_fib")
    validate_pullback = next(s for s in hydrated.steps if s.step_definition.id == "validate_pullback")

    assert isinstance(check_fib, StrategyStepInstance)
    assert check_fib.runtime_bindings["trend"] == "trend"
    assert check_fib.reevaluates[0] is validate_pullback.step_definition


def test_missing_step_definition_raises(raw_strategy_dict):
    raw_config = RawStrategyConfig(**raw_strategy_dict)
    mock_service = Mock()
    mock_service.get.return_value = None  # Simulate missing

    with pytest.raises(ValueError, match="Step definition with id 'check_fib' not found in StrategyStepService"):
        hydrate_strategy_config(raw_config, mock_service)


def test_missing_reevaluated_step_instance_raises(raw_strategy_dict, mock_step_service):
    # Remove reevaluated step from strategy dict
    raw_strategy_dict["steps"] = [raw_strategy_dict["steps"][0]]  # Only check_fib

    raw_config = RawStrategyConfig(**raw_strategy_dict)

    with pytest.raises(ValueError, match="Reevaluated step id 'validate_pullback' not found in strategy steps"):
        hydrate_strategy_config(raw_config, mock_step_service)