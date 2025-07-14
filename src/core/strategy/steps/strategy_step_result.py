from datetime import datetime

import pandas as pd
import pytest

from core.strategy.steps.model import StrategyStepResult


def test_strategy_step_result_ok():
    # Given
    outputs = {"signal": "buy", "score": 0.92}
    price_index = pd.Timestamp("2024-01-15T10:00:00")

    # When
    result = StrategyStepResult.ok(outputs=outputs, price_index=price_index)

    # Then
    assert result.success is True
    assert result.outputs == outputs
    assert result.price_index == price_index
    assert result.message is None
    assert isinstance(result.result_time, datetime)


def test_strategy_step_result_err_with_stack():
    # Given
    message = "Failed to fetch data"
    stack = "Traceback (most recent call last): ..."

    # When
    result = StrategyStepResult.err(message=message, stack=stack)

    # Then
    assert result.success is False
    assert result.message == message
    assert result.outputs == {}
    assert result.price_index is None
    assert result.stack_trace == stack


def test_strategy_step_result_err_without_stack():
    # When
    result = StrategyStepResult.err("Invalid input")

    # Then
    assert result.success is False
    assert result.message == "Invalid input"
    assert result.stack_trace is None


def test_from_result_ok_creates_success_result():
    class Ok:
        def __init__(self, value):
            self.value = value
    
    result = Ok({"foo": 123})
    step_result = StrategyStepResult.from_result(result)

    assert step_result.success is True
    assert step_result.outputs == {"foo": 123}
    assert step_result.message is None


def test_from_result_err_creates_failure_result():
    class Err:
        def __init__(self, error):
            self.error = error

    try:
        raise ValueError("Something went wrong")
    except ValueError as e:
        result = Err(e)
        step_result = StrategyStepResult.from_result(result)

    assert step_result.success is False
    assert "Something went wrong" in step_result.message
    assert step_result.outputs == {}
    assert step_result._stack and "ValueError" in step_result._stack


def test_from_result_invalid_type_raises():
    class Invalid:
        pass

    result = Invalid()

    with pytest.raises(TypeError):
        StrategyStepResult.from_result(result)


def test_from_result_preserves_price_index():
    import pandas as pd
    class Ok:
        def __init__(self, value):
            self.value = value

    ts = pd.Timestamp("2024-01-01T12:00:00")
    result = Ok({"output": 1})
    step_result = StrategyStepResult.from_result(result, price_index=ts)

    assert step_result.price_index == ts