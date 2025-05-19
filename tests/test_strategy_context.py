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


#region Adding results
def test_add_single_result(step1, ts1):
    context = StrategyExecutionContext() 
    result = StrategStepEvaluationResult(is_success=True, message="OK", step_output={"key1": "value1"})
    key = (ts1, step1)

    return_value = context.add_result(ts1, step1, result)
    
    assert return_value is None 
    # single item in results history and cache
    assert len(context.strategy_steps_results) == 1 
    assert len(context._latest_results_cache) == 1 

    assert key in context.strategy_steps_results
    
    assert context.strategy_steps_results[key] == result 


def test_add_multiple_unique_results(step1, step2, ts1, ts2):
    context = StrategyExecutionContext() # Use V2
    result1 = StrategStepEvaluationResult(is_success=True, message="OK1", step_output={"key1": "value1"})
    result2 = StrategStepEvaluationResult(is_success=True, message="OK2", step_output={"key2": "value2"})
    
    key1 = (ts1, step1)
    key2 = (ts2, step2) 

    # Add first result
    context.add_result(ts1, step1, result1)
    assert len(context.strategy_steps_results) == 1 
    assert len(context._latest_results_cache) == 1 
    
    # Add second result
    context.add_result(ts2, step2, result2)

    # Assert final state
    assert len(context.strategy_steps_results) == 2
    assert len(context._latest_results_cache) == 2

    assert key1 in context.strategy_steps_results
    assert key2 in context.strategy_steps_results
    
    assert context.strategy_steps_results[key1] == result1
    assert context.strategy_steps_results[key2] == result2


def test_add_overwriting_result(step1, ts1, ts2):
    """Test that adding a new result from the same step overwrites the previous value in cache."""
    context = StrategyExecutionContext()
    
    # First result from step1
    result1 = StrategStepEvaluationResult(
        is_success=True, 
        message="First run", 
        step_output={"trend": "UP"}
    )
    
    # Second result from same step (step1) with different output
    result2 = StrategStepEvaluationResult(
        is_success=True, 
        message="Second run", 
        step_output={"trend": "DOWN"}
    )
    
    # Add first result
    context.add_result(ts1, step1, result1)
    assert len(context.strategy_steps_results) == 1
    assert len(context._latest_results_cache) == 1
    assert context._latest_results_cache["trend"] == "UP"
    
    # Add second result from same step
    context.add_result(ts2, step1, result2)
    
    # History should have both results
    assert len(context.strategy_steps_results) == 2
    
    # Cache should still have one entry but with updated value
    assert len(context._latest_results_cache) == 1
    assert context._latest_results_cache["trend"] == "DOWN"
    
    # Both results should be in history
    key1 = (ts1, step1)
    key2 = (ts2, step1)
    assert context.strategy_steps_results[key1] == result1
    assert context.strategy_steps_results[key2] == result2 

#endregion

@pytest.mark.skip(reason="Temporarily skipped during refactoring")
def test_find_latest_successful_data_latest_failed_v2(step1, step2, ts1, ts2):
    """Test finding data when the latest step with the key failed (V2).
    NOTE: This test assumes the *intended* logic of find_latest_successful_data.
    """
    context = StrategyExecutionContext() # Use V2
    result1 = StrategStepEvaluationResult(is_success=True, message="OK1", step_output={"key1": "value1_ok"})
    result2 = StrategStepEvaluationResult(is_success=False, message="Fail2", step_output={"key1": "value2_fail"})
    
    context.add_result(ts1, step1, result1)
    context.add_result(ts2, step2, result2)
    
    # The find method should still look back chronologically for the latest *successful* result
    found_data = context.get_latest_strategey_step_output_result("key1")
    assert found_data == "value1_ok" 


@pytest.mark.skip(reason="Temporarily skipped during refactoring")
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
        is_success=True, message="Step 1 ok", step_output=data_payload_1
    )
    result2 = StrategStepEvaluationResult(
        is_success=True, message="Step 2 ok", step_output=data_payload_2  # Same data payload
    )
    result3_diff_name = StrategStepEvaluationResult(
        is_success=True, message="Step 1 diff name ok", step_output=data_payload_3
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
    assert key3_diff_name in context.strategy_steps_results # Verify it was added
    assert len(context.strategy_steps_results) == 2

    # Adding the same data payload from a *different* step (different ID) should raise error
    # Match against the error message format which now uses step name/id
    with pytest.raises(ValueError, match=rf"Step '{dummy_strategy_step.name}' \(ID: {dummy_strategy_step.id}\)"):
        context.add_result(timestamp2, dummy_strategy_step_2, result2)
        
    # Verify context was not modified by the failed call
    assert len(context.strategy_steps_results) == 2 # Still 2 entries
    assert key1 in context.strategy_steps_results
    assert key3_diff_name in context.strategy_steps_results
    assert key2 not in context.strategy_steps_results # Check the second key wasn't added


@pytest.mark.skip(reason="Temporarily skipped during refactoring")
def test_strategy_execution_context_add_result_duplicate_data_same_step_v2():
    """Tests adding duplicate data from the *same* step is allowed (V2)."""
    step_id = "step_same_data"
    step = StrategyStep(id=step_id, name="SameDataStep", description="Desc", evaluation_fn=lambda df, ctx, cfg: None, config={})
    timestamp1 = pd.Timestamp("2023-01-01 10:00:00")
    timestamp2 = pd.Timestamp("2023-01-01 10:05:00")
    data_payload = {"key1": "value1", "key2": 123}

    result1 = StrategStepEvaluationResult(
        is_success=True, message="Step 1 ok", step_output=data_payload
    )
    result2 = StrategStepEvaluationResult(
        is_success=True, message="Step 2 ok", step_output=data_payload  # Same data
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
    assert len(context.strategy_steps_results) == 2
    assert key1 in context.strategy_steps_results
    assert key2 in context.strategy_steps_results
    # In V2, the key contains the step object, the value is just the result
    assert context.strategy_steps_results[key1].step_output == data_payload
    assert context.strategy_steps_results[key2].step_output == data_payload 

@pytest.mark.skip(reason="Temporarily skipped during refactoring")
def test_validate_no_duplicate_outputs_success():
    """Test that different steps with different outputs pass validation"""
    context = StrategyExecutionContext()
    
    # Create two different steps
    step1 = StrategyStep(
        id="step1",
        name="Step 1",
        evaluation_fn=lambda x, y, z: None  # dummy function
    )
    
    step2 = StrategyStep(
        id="step2",
        name="Step 2",
        evaluation_fn=lambda x, y, z: None  # dummy function
    )
    
    # Create results with different outputs
    result1 = StrategStepEvaluationResult(
        is_success=True,
        step_output={"key1": "value1"}
    )
    
    result2 = StrategStepEvaluationResult(
        is_success=True,
        step_output={"key2": "value2"}
    )
    
    # This should not raise an exception
    context._validate_no_duplicate_outputs_by_different_steps(
        step1,
        result1,
        {(None, step2): result2}
    )

@pytest.mark.skip(reason="Temporarily skipped during refactoring")
def test_validate_no_duplicate_outputs_failure():
    """Test that different steps with identical outputs raise ValueError"""
    context = StrategyExecutionContext()
    
    # Create two different steps
    step1 = StrategyStep(
        id="step1",
        name="Step 1",
        evaluation_fn=lambda x, y, z: None  # dummy function
    )
    
    step2 = StrategyStep(
        id="step2",
        name="Step 2",
        evaluation_fn=lambda x, y, z: None  # dummy function
    )
    
    # Create results with identical outputs
    same_output = {"key": "value"}
    result1 = StrategStepEvaluationResult(
        is_success=True,
        step_output=same_output
    )
    
    result2 = StrategStepEvaluationResult(
        is_success=True,
        step_output=same_output
    )
    
    # This should raise a ValueError
    with pytest.raises(ValueError) as exc_info:
        context._validate_no_duplicate_outputs_by_different_steps(
            step1,
            result1,
            {(None, step2): result2}
        )
    
    # Verify the error message
    assert "produced identical output" in str(exc_info.value)
    assert "Step 1" in str(exc_info.value)
    assert "Step 2" in str(exc_info.value)

@pytest.mark.skip(reason="Temporarily skipped during refactoring")
def test_validate_no_duplicate_outputs_empty():
    """Test that steps with empty outputs pass validation"""
    context = StrategyExecutionContext()
    
    step = StrategyStep(
        id="step1",
        name="Step 1",
        evaluation_fn=lambda x, y, z: None  # dummy function
    )
    
    # Create result with empty output
    result = StrategStepEvaluationResult(
        is_success=True,
        step_output={}
    )
    
    # This should not raise an exception
    context._validate_no_duplicate_outputs_by_different_steps(
        step,
        result,
        {}  # empty previous results
    )

@pytest.mark.skip(reason="Temporarily skipped during refactoring")
def test_validate_no_duplicate_outputs_none():
    """Test that steps with None outputs pass validation"""
    context = StrategyExecutionContext()
    
    step = StrategyStep(
        id="step1",
        name="Step 1",
        evaluation_fn=lambda x, y, z: None  # dummy function
    )
    
    # Create result with None output
    result = StrategStepEvaluationResult(
        is_success=True,
        step_output=None
    )
    
    # This should not raise an exception
    context._validate_no_duplicate_outputs_by_different_steps(
        step,
        result,
        {}  # empty previous results
    )

