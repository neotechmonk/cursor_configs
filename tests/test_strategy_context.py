# tests/test_strategy_execution_context_v2.py

"""Tests specifically for the StrategyExecutionContextV2 class."""

import pandas as pd
import pytest

# Imports from strategy module needed for tests
# Update import for StrategStepEvaluationResult and StrategyExecutionContextV2
from models import StrategStepEvaluationResult, StrategyExecutionContext, StrategyStep


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

# --- Tests for V2 --- 


def test_add_result_initial_v2(step1, ts1):
    """Test adding the first result to an empty context (V2)."""
    context = StrategyExecutionContext() # Use V2
    result = StrategStepEvaluationResult(success=True, message="OK", data={"key1": "value1"})
    
    # Call add_result (modifies context in-place, returns None)
    return_value = context.add_result(ts1, step1, result)
    
    # Assert modification happened in place
    assert return_value is None # Check return value is None as per mutable implementation
    key = (ts1, step1) # V2 uses (timestamp, step object) as key
    assert len(context.result_history) == 1
    assert key in context.result_history
    assert context.result_history[key] == result # Value is just the result


def test_add_result_multiple_v2(step1, step2, ts1, ts2):
    """Test adding multiple distinct results (V2)."""
    context = StrategyExecutionContext() # Use V2
    result1 = StrategStepEvaluationResult(success=True, message="OK1", data={"key1": "value1"})
    result2 = StrategStepEvaluationResult(success=True, message="OK2", data={"key2": "value2"})
    
    # Add first result
    context.add_result(ts1, step1, result1)
    assert len(context.result_history) == 1 # Check immediate effect
    
    # Add second result
    context.add_result(ts2, step2, result2)
    
    key1 = (ts1, step1) # V2 uses (timestamp, step object) as key
    key2 = (ts2, step2) # V2 uses (timestamp, step object) as key
    
    # Assert final state
    assert len(context.result_history) == 2
    assert key1 in context.result_history
    assert key2 in context.result_history
    assert context.result_history[key1] == result1
    assert context.result_history[key2] == result2


def test_find_latest_successful_data_latest_failed_v2(step1, step2, ts1, ts2):
    """Test finding data when the latest step with the key failed (V2).
    NOTE: This test assumes the *intended* logic of find_latest_successful_data.
    """
    context = StrategyExecutionContext() # Use V2
    result1 = StrategStepEvaluationResult(success=True, message="OK1", data={"key1": "value1_ok"})
    result2 = StrategStepEvaluationResult(success=False, message="Fail2", data={"key1": "value2_fail"})
    
    context.add_result(ts1, step1, result1)
    context.add_result(ts2, step2, result2)
    
    # The find method should still look back chronologically for the latest *successful* result
    found_data = context.find_latest_successful_data("key1")
    assert found_data == "value1_ok" 


def test_strategy_execution_context_add_result_duplicate_data_v2():
    """Tests that adding a result with duplicate data raises ValueError (V2).
    NOTE: The validation logic in V2 now uses step object equality.
    """
    dummy_strategy_step = StrategyStep(
        id="step_dup_1", 
        name="StepDup1",
        description="Test Step Dup 1",
        evaluation_fn=lambda df, ctx, cfg: None,
        config={}
    )
    # Create a step that differs only in name/desc (but same ID) - should NOT cause collision
    dummy_strategy_step_diff_name = StrategyStep(
        id="step_dup_1", 
        name="StepDup1 Different Name", 
        description="Test Step Dup 1",
        evaluation_fn=lambda df, ctx, cfg: None,
        config={}
    )
    # Create a truly different step
    dummy_strategy_step_2 = StrategyStep(
        id="step_dup_2",
        name="StepDup2",
        description="Test Step Dup 2",
        evaluation_fn=lambda df, ctx, cfg: None,
        config={}
    )
    timestamp1 = pd.Timestamp("2023-01-01 10:00:00")
    timestamp2 = pd.Timestamp("2023-01-01 10:05:00")
    timestamp3 = pd.Timestamp("2023-01-01 10:10:00") # For step_diff_name
    data_payload_1 = {"key1": "value1", "key2": 123}
    data_payload_2 = {"key1": "value1", "key2": 123} # Identical payload
    data_payload_3 = {"keyA": "valueA"} # Different payload

    result1 = StrategStepEvaluationResult(
        success=True, message="Step 1 ok", data=data_payload_1
    )
    result2 = StrategStepEvaluationResult(
        success=True, message="Step 2 ok", data=data_payload_2  # Same data payload
    )
    result3_diff_name = StrategStepEvaluationResult(
        success=True, message="Step 1 diff name ok", data=data_payload_3
    )

    context = StrategyExecutionContext() # Use V2
    key1 = (timestamp1, dummy_strategy_step)
    key2 = (timestamp2, dummy_strategy_step_2)
    key3_diff_name = (timestamp3, dummy_strategy_step_diff_name)
    
    # Add first result successfully
    context.add_result(timestamp1, dummy_strategy_step, result1)
    
    # Add result from step with different name/desc but same ID (should be OK)
    try:
        context.add_result(timestamp3, dummy_strategy_step_diff_name, result3_diff_name)
    except ValueError as e:
        pytest.fail(f"Adding result from step with different name/desc but same ID raised unexpected ValueError: {e}")
    assert key3_diff_name in context.result_history # Verify it was added
    assert len(context.result_history) == 2

    # Adding the same data payload from a *different* step (different ID) should raise error
    # Match against the error message format which now uses step name/id
    with pytest.raises(ValueError, match=rf"Step '{dummy_strategy_step.name}' \(ID: {dummy_strategy_step.id}\)"):
        context.add_result(timestamp2, dummy_strategy_step_2, result2)
        
    # Verify context was not modified by the failed call
    assert len(context.result_history) == 2 # Still 2 entries
    assert key1 in context.result_history
    assert key3_diff_name in context.result_history
    assert key2 not in context.result_history # Check the second key wasn't added


def test_strategy_execution_context_add_result_duplicate_data_same_step_v2():
    """Tests adding duplicate data from the *same* step is allowed (V2)."""
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

    context = StrategyExecutionContext() # Use V2
    key1 = (timestamp1, step) # Use step object
    key2 = (timestamp2, step) # Use step object

    # Add first result
    context.add_result(timestamp1, step, result1)

    # Adding the same data payload from the *same* step object should be allowed
    try:
        context.add_result(timestamp2, step, result2) # Use the same step object
    except ValueError as e:
        pytest.fail(f"Adding duplicate data from the same step raised an unexpected ValueError: {e}")

    # Check history contains both entries (context modified in place)
    assert len(context.result_history) == 2
    assert key1 in context.result_history
    assert key2 in context.result_history
    # In V2, the key contains the step object, the value is just the result
    assert context.result_history[key1].data == data_payload
    assert context.result_history[key2].data == data_payload 