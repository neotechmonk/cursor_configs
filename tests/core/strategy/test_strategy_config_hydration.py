import pytest

from core.strategy.hydration import hydrate_strategy_config
from core.strategy.model import (
    RawStrategyConfig,
    StrategyConfig,
    StrategyStepDefinition,
    StrategyStepInstance,
)


@pytest.fixture
def mock_step_registry():
    """Mocked step registry with two step definitions."""
    return {
        "check_fib": StrategyStepDefinition(
            id="check_fib",
            function_path="mock.module.check_fib",
            input_bindings={},
            output_bindings={"result": StrategyStepDefinition.OutputBinding(mapping="_")}
        ),
        "validate_pullback": StrategyStepDefinition(
            id="validate_pullback",
            function_path="mock.module.validate_pullback",
            input_bindings={},
            output_bindings={"valid": StrategyStepDefinition.OutputBinding(mapping="_")}
        ),
    }


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


def test_hydrate_strategy_config_success(raw_strategy_dict, mock_step_registry):
    raw_config = RawStrategyConfig(**raw_strategy_dict)
    hydrated = hydrate_strategy_config(raw_config, mock_step_registry)

    assert isinstance(hydrated, StrategyConfig)
    assert hydrated.name == "Trend Following Strategy"
    assert len(hydrated.steps) == 2

    check_fib = next(s for s in hydrated.steps if s.id.id == "check_fib")
    validate_pullback = next(s for s in hydrated.steps if s.id.id == "validate_pullback")

    assert isinstance(check_fib, StrategyStepInstance)
    assert check_fib.runtime_bindings["trend"] == "trend"

    # Check that reevaluation is linked to the actual instance
    assert len(check_fib.reevaluates) == 1
    assert check_fib.reevaluates[0] is validate_pullback  # Reference, not just same ID


def test_hydrate_strategy_config_missing_step_definition(raw_strategy_dict):
    raw_config = RawStrategyConfig(**raw_strategy_dict)
    # Remove both step definitions
    empty_registry = {}

    with pytest.raises(ValueError, match="Step definition with id 'check_fib' not found"):
        hydrate_strategy_config(raw_config, empty_registry)


def test_hydrate_strategy_config_missing_reevaluation_instance(mock_step_registry):
    # Only 1 step, reevaluates points to a non-existent step in the strategy
    bad_raw_dict = {
        "name": "Invalid Reeval",
        "steps": [
            {
                "id": "check_fib",
                "description": "Check Fibonacci criteria",
                "config_bindings": {},
                "runtime_bindings": {},
                "reevaluates": ["validate_pullback"]  # Not present in strategy steps
            }
        ]
    }

    raw_config = RawStrategyConfig(**bad_raw_dict)

    with pytest.raises(ValueError, match="Reevaluated step id 'validate_pullback' not found in strategy steps"):
        hydrate_strategy_config(raw_config, mock_step_registry)