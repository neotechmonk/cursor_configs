

from core.strategy.steps.model import StrategyStepDefinition


def test_strategy_step_definition_happy_path():
    config = {
        "id": "check_fib",
        "function_path": "calculate_fib_valid",
        "input_bindings": {
            "trend": {
                "source": "context",
                "lookup_name": "trend"
            },
            "ref_swing_start_idx": {
                "source": "context",
                "lookup_name": "start"
            },
            "ref_swing_end_idx": {
                "source": "context",
                "lookup_name": "end"
            },
            "min_ratio": {
                "source": "config",
                "lookup_name": "fib_ratio_threshold"
            }
        },
        "output_bindings": {
            "fib_valid": {
                "target_name": "_"
            }
        }
    }

    step = StrategyStepDefinition(**config)

    assert step.id == "check_fib"
    assert step.function_path == "calculate_fib_valid"

    assert step.input_bindings["trend"].source == StrategyStepDefinition.ParamSource.CONTEXT
    assert step.input_bindings["trend"].lookup_name == "trend"

    assert step.input_bindings["min_ratio"].source == StrategyStepDefinition.ParamSource.CONFIG
    assert step.input_bindings["min_ratio"].lookup_name == "fib_ratio_threshold"

    # Check that '_' is mapped to None
    assert step.output_bindings["fib_valid"].target_name is None