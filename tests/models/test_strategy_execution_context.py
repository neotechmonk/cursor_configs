import pandas as pd
import pytest

from src.models.strategy import (
    StrategyExecutionContext,
    StrategyStep,
    StrategyStepEvaluationResult,
)


@pytest.fixture
def step1() -> StrategyStep:
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


def test_add_single_result(step1, ts1):
    context = StrategyExecutionContext()
    result = StrategyStepEvaluationResult(is_success=True, message="OK", step_output={"key1": "value1"})
    key = (ts1, step1)
    context.add_result(ts1, step1, result)
    assert len(context.strategy_steps_results) == 1
    assert len(context.latest_results_cache) == 1
    assert key in context.strategy_steps_results
    assert context.strategy_steps_results[key] == result


def test_add_multiple_unique_results(step1, step2, ts1, ts2):
    context = StrategyExecutionContext()
    result1 = StrategyStepEvaluationResult(is_success=True, message="OK1", step_output={"key1": "value1"})
    result2 = StrategyStepEvaluationResult(is_success=True, message="OK2", step_output={"key2": "value2"})
    key1 = (ts1, step1)
    key2 = (ts2, step2)
    context.add_result(ts1, step1, result1)
    assert len(context.strategy_steps_results) == 1
    assert len(context.latest_results_cache) == 1
    context.add_result(ts2, step2, result2)
    assert len(context.strategy_steps_results) == 2
    assert len(context.latest_results_cache) == 2
    assert key1 in context.strategy_steps_results
    assert key2 in context.strategy_steps_results
    assert context.strategy_steps_results[key1] == result1
    assert context.strategy_steps_results[key2] == result2


def test_add_overwriting_result_upon_success(step1, ts1, ts2):
    context = StrategyExecutionContext()
    result1 = StrategyStepEvaluationResult(is_success=True, message="First run", step_output={"trend": "UP"})
    result2 = StrategyStepEvaluationResult(is_success=True, message="Second run", step_output={"trend": "DOWN"})
    context.add_result(ts1, step1, result1)
    assert len(context.strategy_steps_results) == 1
    assert len(context.latest_results_cache) == 1
    assert context.latest_results_cache["trend"] == "UP"
    context.add_result(ts2, step1, result2)
    assert len(context.strategy_steps_results) == 2
    assert len(context.latest_results_cache) == 1
    assert context.latest_results_cache["trend"] == "DOWN"
    key1 = (ts1, step1)
    key2 = (ts2, step1)
    assert context.strategy_steps_results[key1] == result1
    assert context.strategy_steps_results[key2] == result2


def test_preserve_successful_result_upon_sebsequent_failure(step1, ts1, ts2):
    context = StrategyExecutionContext()
    result_success = StrategyStepEvaluationResult(is_success=True, message="First run successful", step_output={"trend": "UP"})
    result_failure = StrategyStepEvaluationResult(is_success=False, message="Second run failed", step_output={"trend": "DOWN"})
    context.add_result(ts1, step1, result_success)
    assert len(context.strategy_steps_results) == 1
    assert len(context.latest_results_cache) == 1
    assert context.latest_results_cache["trend"] == "UP"
    context.add_result(ts2, step1, result_failure)
    assert len(context.strategy_steps_results) == 2
    assert len(context.latest_results_cache) == 1
    assert context.latest_results_cache["trend"] == "UP"
    key1 = (ts1, step1)
    key2 = (ts2, step1)
    assert context.strategy_steps_results[key1] == result_success
    assert context.strategy_steps_results[key2] == result_failure
    latest_result = context.get_latest_strategey_step_output_result("trend")
    assert latest_result == "UP"


def test_reject_duplicate_output_from_different_steps():
    """Test that adding the same output from different steps raises ValueError."""
    # Create two different steps
    step1 = StrategyStep(
        id="step1",
        name="Step One",
        description="First step",
        evaluation_fn=lambda df, ctx, cfg: None,
        config={}
    )
    
    step2 = StrategyStep(
        id="step2",
        name="Step Two",
        description="Second step",
        config={},
        evaluation_fn=lambda df, ctx, cfg: None
    )
    
    # Create timestamps
    ts1 = pd.Timestamp("2023-01-01 10:00:00")
    ts2 = pd.Timestamp("2023-01-01 10:01:00")
    
    # Create results with identical output
    same_output = {"trend": "UP", "strength": "HIGH"}
    result1 = StrategyStepEvaluationResult(
        is_success=True,
        message="Step 1 result",
        step_output=same_output
    )
    
    result2 = StrategyStepEvaluationResult(
        is_success=True,
        message="Step 2 result",
        step_output=same_output  # Same output as step1
    )
    
    context = StrategyExecutionContext()
    
    # Add first result successfully
    context.add_result(ts1, step1, result1)
    assert len(context.strategy_steps_results) == 1
    assert len(context.latest_results_cache) == 2  # Two keys in output
    
    # Attempting to add same output from different step should raise ValueError
    with pytest.raises(ValueError, match="cannot produce the same output"):
        context.add_result(ts2, step2, result2)
    
    # Verify context was not modified by the failed call
    assert len(context.strategy_steps_results) == 1
    assert len(context.latest_results_cache) == 2
    assert (ts1, step1) in context.strategy_steps_results
    assert (ts2, step2) not in context.strategy_steps_results 