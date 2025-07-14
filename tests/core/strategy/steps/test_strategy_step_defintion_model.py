import types
from typing import Callable

import pytest

from core.strategy.steps.model import StrategyStepDefinition

# ----------------------------
# MOCK FUNCTION DEFINITIONS
# ----------------------------


def dummy_function(arg1, arg2):
    return {"result": arg1 + arg2}


def dummy_function_missing_args():
    return {"result": 0}


# ----------------------------
# MOCK LOADER FOR PATCHING
# ----------------------------

def fake_loader(path: str) -> Callable:
    if path == "mock.module.valid_func":
        return dummy_function
    elif path == "mock.module.bad_func":
        return dummy_function_missing_args
    else:
        raise ImportError(f"No such function: {path}")


# ----------------------------
# PATCHED MODEL WITH FAKE LOADER
# ----------------------------

@pytest.fixture(autouse=True)
def patch_loader(monkeypatch):
    # Patch your load_function utility to our fake_loader
    monkeypatch.setattr("core.strategy.steps.model.function_loader", fake_loader)


# ----------------------------
# TESTS
# ----------------------------

def test_valid_strategy_step_definition():
    step = StrategyStepDefinition(
        id="step_add",
        function_path="mock.module.valid_func",
        input_bindings={
            "arg1": StrategyStepDefinition.InputBinding(source="config", mapping="a"),
            "arg2": StrategyStepDefinition.InputBinding(source="runtime", mapping="b"),
        },
        output_bindings={
            "result": StrategyStepDefinition.OutputBinding(mapping="sum")
        }
    )

    func = step.callable_fn
    assert isinstance(func, types.FunctionType)
    assert func(3, 4) == {"result": 7}


def test_missing_function_param_validation():
    with pytest.raises(ValueError) as exc_info:
        StrategyStepDefinition(
            id="step_fail",
            function_path="mock.module.bad_func",
            input_bindings={
                "arg1": StrategyStepDefinition.InputBinding(source="config", mapping="a")
            },
            output_bindings={}
        )

    assert "missing params" in str(exc_info.value)


def test_output_binding_mapping_underscore_converted_to_none():
    step = StrategyStepDefinition(
        id="step_out",
        function_path="mock.module.valid_func",
        input_bindings={
            "arg1": StrategyStepDefinition.InputBinding(source="config", mapping="a"),
            "arg2": StrategyStepDefinition.InputBinding(source="config", mapping="b"),
        },
        output_bindings={
            "value": StrategyStepDefinition.OutputBinding(mapping="_")
        }
    )

    assert step.output_bindings["value"].mapping is None