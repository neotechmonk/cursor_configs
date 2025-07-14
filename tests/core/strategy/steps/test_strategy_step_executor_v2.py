import pytest
from unittest.mock import patch
from core.strategy.steps.model import StrategyStepDefinition

# --- Mock functions declared in this module ---

def valid_fn(trend, ref_swing_start_idx, ref_swing_end_idx, min_ratio):
    return {"fib_valid": True}

def minimal_valid_fn(trend):
    return {"fib_valid": True}

def missing_param_fn():
    return {"result": "no params"}

def invalid_result_fn(trend):
    return ["not", "a", "dict"]

# --- Tests ---

def test_strategy_step_definition_happy_path():
    fn = valid_fn
    fn_path = f"{fn.__module__}.{fn.__name__}"

    config = {
        "id": "check_fib",
        "function_path": fn_path,
        "input_bindings": {
            "trend": {"source": "runtime", "mapping": "trend"},
            "ref_swing_start_idx": {"source": "runtime", "mapping": "start"},
            "ref_swing_end_idx": {"source": "runtime", "mapping": "end"},
            "min_ratio": {"source": "config", "mapping": "fib_ratio_threshold"},
        },
        "output_bindings": {
            "fib_valid": {"mapping": "_"},
        },
    }

    step = StrategyStepDefinition(**config)

    assert step.id == "check_fib"
    assert step.function_path.endswith("valid_fn")
    assert step.input_bindings["trend"].source == StrategyStepDefinition.ParamSource.RUNTIME
    assert step.input_bindings["trend"].mapping == "trend"
    assert step.input_bindings["min_ratio"].source == StrategyStepDefinition.ParamSource.CONFIG
    assert step.input_bindings["min_ratio"].mapping == "fib_ratio_threshold"
    assert step.output_bindings["fib_valid"].mapping is None


def test_strategy_step_definition_conflicting_sources_raises_error():
    with pytest.raises(ValueError, match="Duplicate input mappings found"):
        StrategyStepDefinition(
            id="conflict_step",
            function_path="tests.core.strategy.steps.test_strategy_step_definition_model.valid_fn",
            input_bindings={
                "param_from_runtime": StrategyStepDefinition.InputBinding(
                    source="runtime", mapping="shared_key"
                ),
                "param_from_config": StrategyStepDefinition.InputBinding(
                    source="config", mapping="shared_key"
                ),
            },
            output_bindings={},
            _validate_signature=False,
            _validate_result_protocol=False,
        )

    with pytest.raises(ValueError, match="Duplicate input mappings found"):
        StrategyStepDefinition(
            id="conflict_step",
            function_path="tests.core.strategy.steps.test_strategy_step_definition_model.valid_fn",
            input_bindings={
                "param1": StrategyStepDefinition.InputBinding(
                    source="runtime", mapping="shared_key"
                ),
                "param2": StrategyStepDefinition.InputBinding(
                    source="runtime", mapping="shared_key"
                ),
            },
            output_bindings={},
            _validate_signature=False,
            _validate_result_protocol=False,
        )


def test_signature_validation_raises():
    fn = missing_param_fn
    fn_path = f"{fn.__module__}.{fn.__name__}"
    config = {
        "id": "missing_param",
        "function_path": fn_path,
        "input_bindings": {
            "trend": {"source": "runtime", "mapping": "trend"},
            "min_ratio": {"source": "config", "mapping": "fib"},
        },
        "output_bindings": {
            "fib_valid": {"mapping": "_"},
        },
    }

    with pytest.raises(ValueError, match="missing params"):
        StrategyStepDefinition(**config)


def test_result_protocol_validation_raises():
    fn = invalid_result_fn
    fn_path = f"{fn.__module__}.{fn.__name__}"
    config = {
        "id": "invalid_result",
        "function_path": fn_path,
        "input_bindings": {
            "trend": {"source": "runtime", "mapping": "trend"},
        },
        "output_bindings": {
            "some_key": {"mapping": "_"},
        },
        "_validate_result_protocol": True,
        "_validate_signature": False,
    }

    with pytest.raises(ValueError, match="does not conform to ResultProtocol"):
        StrategyStepDefinition(**config)


def test_strategy_step_definition_minimal_without_validation():

    class TestableStrategyStepDefinition(StrategyStepDefinition):
        def __init__(self, *args, _validate_signature=True, _validate_result_protocol=False, **kwargs):
            super().__init__(*args, **kwargs)
            self._validate_signature = _validate_signature
            self._validate_result_protocol = _validate_result_protocol
    fn = minimal_valid_fn
    fn_path = f"{fn.__module__}.{fn.__name__}"

    config = {
        "id": "minimal",
        "function_path": fn_path,
        "input_bindings": {
            "trend": {"source": "runtime", "mapping": "trend"},
        },
        "output_bindings": {
            "fib_valid": {"mapping": "_"},
        }
    }

    step = TestableStrategyStepDefinition(
        **config,
        _validate_signature=False,
        _validate_result_protocol=False
    )

    assert callable(step.callable_fn)