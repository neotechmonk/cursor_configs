import pytest

from core.strategy.steps.model import StrategyStepDefinition


def test_strategy_step_definition_happy_path():
    config = {
        "id": "check_fib",
        "function_path": "calculate_fib_valid",
        "input_bindings": {
            "trend": {
                "source": "runtime",
                "mapping": "trend"
            },
            "ref_swing_start_idx": {
                "source": "runtime",
                "mapping": "start"
            },
            "ref_swing_end_idx": {
                "source": "runtime",
                "mapping": "end"
            },
            "min_ratio": {
                "source": "config",
                "mapping": "fib_ratio_threshold"
            }
        },
        "output_bindings": {
            "fib_valid": {
                "mapping": "_"
            }
        }
    }

    step = StrategyStepDefinition(**config)

    assert step.id == "check_fib"
    assert step.function_path == "calculate_fib_valid"

    assert step.input_bindings["trend"].source == StrategyStepDefinition.ParamSource.RUNTIME
    assert step.input_bindings["trend"].mapping == "trend"

    assert step.input_bindings["min_ratio"].source == StrategyStepDefinition.ParamSource.CONFIG
    assert step.input_bindings["min_ratio"].mapping == "fib_ratio_threshold"

    # Check that '_' is mapped to None
    assert step.output_bindings["fib_valid"].mapping is None


def test_strategy_step_definition_conflicting_sources_raises_error():
    with pytest.raises(ValueError, match="Duplicate input mappings found"):
        StrategyStepDefinition(
            id="conflict_step",
            function_path="some_module.some_function",
            input_bindings={
                "param_from_runtime": StrategyStepDefinition.InputBinding(source="runtime", mapping="shared_key"),
                "param_from_config": StrategyStepDefinition.InputBinding(source="config", mapping="shared_key"),
            },
            output_bindings={}
        )

    with pytest.raises(ValueError, match="Duplicate input mappings found"):
        StrategyStepDefinition(
            id="conflict_step",
            function_path="some_module.some_function",
            input_bindings={
                "param1_from_runtime": StrategyStepDefinition.InputBinding(source="runtime", mapping="shared_key"),
                "param2_from_runtime": StrategyStepDefinition.InputBinding(source="runtime", mapping="shared_key"),
            },
            output_bindings={}
        )
    