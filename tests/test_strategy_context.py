# tests/test_strategy_context.py

"""Tests specifically for the StrategyExecutionContext class."""

import pandas as pd
import pytest

# Imports from strategy module needed for tests
# Update import for StrategStepEvaluationResult
from models import (
    StrategStepEvaluationResult,
    StrategyExecutionContext,
    StrategyStep,
)

# from dataclasses import dataclass # Not needed if only using fixtures


@pytest.fixture
def step1() -> StrategyStep:
    # Using lambda as it seems sufficient for these tests
    return StrategyStep(id="step1", name="Step One", description="", evaluation_fn=lambda p,c,**kw: None, config={}, reevaluates=[])


@pytest.fixture
def step2() -> StrategyStep:
    return StrategyStep(id="step2", name="Step Two", description="", evaluation_fn=lambda p,c,**kw: None, config={}, reevaluates=[])


@pytest.fixture
def ts1() -> pd.Timestamp:
    return pd.Timestamp("2023-01-01 10:00:00")


@pytest.fixture
def ts2() -> pd.Timestamp:
    return pd.Timestamp("2023-01-01 10:01:00")

# --- Moved Tests --- 


def test_add_result_initial(step1, ts1):
    """Test adding the first result to an empty context."""
    context = StrategyExecutionContext()
    result = StrategStepEvaluationResult(success=True, message="OK", data={"key1": "value1"})
    new_context = context.add_result(ts1, step1, result)
    assert new_context is not context
    assert len(new_context.result_history) == 1
    assert ts1 in new_context.result_history
    assert new_context.result_history[ts1] == (step1, result)
    assert len(context.result_history) == 0


def test_add_result_multiple(step1, step2, ts1, ts2):
    """Test adding multiple distinct results."""
    context = StrategyExecutionContext()
    result1 = StrategStepEvaluationResult(success=True, message="OK1", data={"key1": "value1"})
    result2 = StrategStepEvaluationResult(success=True, message="OK2", data={"key2": "value2"})
    context1 = context.add_result(ts1, step1, result1)
    context2 = context1.add_result(ts2, step2, result2)
    assert len(context2.result_history) == 2
    assert ts1 in context2.result_history
    assert ts2 in context2.result_history
    assert context2.result_history[ts1] == (step1, result1)
    assert context2.result_history[ts2] == (step2, result2)
    assert len(context1.result_history) == 1


def test_find_latest_successful_data_latest_failed(step1, step2, ts1, ts2):
    """Test finding data when the latest step with the key failed."""
    context = StrategyExecutionContext()
    result1 = StrategStepEvaluationResult(success=True, message="OK1", data={"key1": "value1_ok"})
    result2 = StrategStepEvaluationResult(success=False, message="Fail2", data={"key1": "value2_fail"})
    context = context.add_result(ts1, step1, result1)
    context = context.add_result(ts2, step2, result2)
    found_data = context.find_latest_successful_data("key1")
    assert found_data == "value1_ok" 