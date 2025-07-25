from unittest.mock import patch

import pytest

from core.strategy.steps.model import StrategyStepDefinition


# ---- Fixtures ----
@pytest.fixture
def valid_func():
    def calculate_fib_valid(trend, ref_swing_start_idx, ref_swing_end_idx, min_ratio):
        return {"fib_valid": True}
    return calculate_fib_valid


@pytest.fixture
def invalid_func_signature():
    def broken_func(unused):
        return {"fib_valid": True}
    return broken_func


@pytest.fixture
def invalid_result_func() :
    def func_without_result_protocol(trend) -> int:  # test will check if return type int is same as the 
        return 123
    return func_without_result_protocol


# @pytest.fixture
# def invalid_result_func():
    
#     return "func_without_result_protocol"

# ---- Tests ----

def test_strategy_step_definition_happy_path(valid_func):
    config = {
        "id": "check_fib",
        "function_path": "mock.module.calculate_fib_valid",
        "input_bindings": {
            "trend": {"source": "runtime", "mapping": "trend"},
            "ref_swing_start_idx": {"source": "runtime", "mapping": "start"},
            "ref_swing_end_idx": {"source": "runtime", "mapping": "end"},
            "min_ratio": {"source": "config", "mapping": "fib_ratio_threshold"},
        },
        "output_bindings": {
            "fib_valid": {"mapping": "_"}
        }
    }

    with patch("core.strategy.steps.model.function_loader", return_value=valid_func):
        step = StrategyStepDefinition(**config)

    assert step.id == "check_fib"
    assert step.function_path == "mock.module.calculate_fib_valid"
    assert step.input_bindings["trend"].source == StrategyStepDefinition.ParamSource.RUNTIME
    assert step.input_bindings["min_ratio"].source == StrategyStepDefinition.ParamSource.CONFIG
    assert step.output_bindings["fib_valid"].mapping is None  # '_' becomes None
    assert callable(step.callable_fn)


def test_strategy_step_definition_conflicting_input_mappings_raises():
    config = {
        "id": "conflict_step",
        "function_path": "mock.module.dummy",
        "input_bindings": {
            "param1": {"source": "runtime", "mapping": "shared_key"},
            "param2": {"source": "config", "mapping": "shared_key"},
        },
        "output_bindings": {},
    }


    with pytest.raises(ValueError, match="Duplicate input mappings found"):
        StrategyStepDefinition( **config)


def test_strategy_step_definition_signature_mismatch_raises(invalid_func_signature):
    config = {
        "id": "step_broken",
        "function_path": "mock.module.broken_func",
        "input_bindings": {
            "arg1": {"source": "runtime", "mapping": "val"},
            "arg2": {"source": "runtime", "mapping": "other_val"},
        },
        "output_bindings": {},
    }

    with patch("core.strategy.steps.model.function_loader", return_value=invalid_func_signature):
        with pytest.raises(ValueError, match="missing params"):
            StrategyStepDefinition(validate_signature = True,validate_result_protocol = True, **config)
            

def test_strategy_step_definition_result_protocol_check_fails(invalid_result_func):
    config = {
        "id": "step_non_conforming",
        "function_path": invalid_result_func.__module__ + "." + invalid_result_func.__name__,
        "input_bindings": {
            "trend": {"source": "runtime", "mapping": "trend"}
        },
        "output_bindings": {
            "some_key": {"mapping": "_"}
        }
    }

    with patch("core.strategy.steps.model.function_loader", return_value=invalid_result_func):
        with pytest.raises(ValueError, match="does not conform to ResultProtocol"):
            StrategyStepDefinition(validate_result_protocol = True, **config)


def test_get_callable_returns_bound_function(valid_func):
    config = {
        "id": "step_callable",
        "function_path": "mock.module.calculate_fib_valid",
        "input_bindings": {
            "trend": {"source": "runtime", "mapping": "trend"},
            "ref_swing_start_idx": {"source": "runtime", "mapping": "start"},
            "ref_swing_end_idx": {"source": "runtime", "mapping": "end"},
            "min_ratio": {"source": "config", "mapping": "fib_ratio_threshold"},
        },
        "output_bindings": {
            "fib_valid": {"mapping": "_"}
        }
    }

    with patch("core.strategy.steps.model.function_loader", return_value=valid_func):
        step = StrategyStepDefinition(**config)

    func = step.callable_fn
    result = func("up", 1, 5, 0.618)

    assert isinstance(result, dict)
    assert "fib_valid" in result