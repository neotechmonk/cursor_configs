# tests/test_strategy_context.py

"""Tests specifically for the StrategyExecutionContext class."""

import pandas as pd
import pytest

# Imports from strategy module needed for tests
# Update import for StrategStepEvaluationResult
from models import StrategStepEvaluationResult, StrategyExecutionContext, StrategyStep

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


def test_strategy_execution_context_add_result_duplicate_data():
    """Tests that adding a result with duplicate data raises ValueError."""
    
    dummy_strategy_step = StrategyStep(
        id="step2", 
        name="Step2",
        description="Test Step 2",
        evaluation_fn=lambda df, ctx, cfg: None,
        config={}
    )

    dummy_strategy_step_2 = StrategyStep(
        id="step1",
        name="Step1",
        description="Test Step 1",
        evaluation_fn=lambda df, ctx, cfg: None,
        config={}
    )

    timestamp1 = pd.Timestamp("2023-01-01 10:00:00")
    timestamp2 = pd.Timestamp("2023-01-01 10:05:00")
    data_payload = {"key1": "value1", "key2": 123} # same for both StrategySteps

    result1 = StrategStepEvaluationResult(
        success=True, message="Step 1 ok", data=data_payload
    )
    result2 = StrategStepEvaluationResult(
        success=True, message="Step 2 ok", data=data_payload  # Same data
    )

    context = StrategyExecutionContext()
    context = context.add_result(timestamp1, dummy_strategy_step, result1)

    # Adding the same data payload from a *different* step should raise error
    with pytest.raises(ValueError, match="Duplicate result data payload found"):
        context.add_result(timestamp2, dummy_strategy_step_2, result2)


def test_strategy_execution_context_add_result_duplicate_data_same_step():
    """Tests that adding a result with duplicate data from the *same* step is allowed."""
    step_id = "step_same_data"
    step = StrategyStep(id=step_id, name="SameDataStep", description="Desc", evaluation_fn=lambda df, ctx, cfg: None, config={})
    timestamp1 = pd.Timestamp("2023-01-01 10:00:00")
    timestamp2 = pd.Timestamp("2023-01-01 10:05:00")
    data_payload = {"key1": "value1", "key2": 123}

    result1 = StrategStepEvaluationResult(
        success=True, message="Step 1 ok", data=data_payload
    )
    result2 = StrategStepEvaluationResult(
        success=True, message="Step 2 ok", data=data_payload  # Same data
    )

    context = StrategyExecutionContext()
    context = context.add_result(timestamp1, step, result1)

    # Adding the same data payload from the *same* step ID should be allowed
    try:
        context = context.add_result(timestamp2, step, result2)
    except ValueError as e:
        pytest.fail(f"Adding duplicate data from the same step raised an unexpected ValueError: {e}")

    # Check history contains both entries
    assert len(context.result_history) == 2
    assert timestamp1 in context.result_history
    assert timestamp2 in context.result_history
    assert context.result_history[timestamp1][0].id == step_id
    assert context.result_history[timestamp2][0].id == step_id
    assert context.result_history[timestamp1][1].data == data_payload
    assert context.result_history[timestamp2][1].data == data_payload
