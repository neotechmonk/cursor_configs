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
    assert len(context._strategy_steps_results) == 1 
    assert len(context._latest_results_cache) == 1 

    assert key in context._strategy_steps_results
    
    assert context._strategy_steps_results[key] == result 


def test_add_multiple_unique_results(step1, step2, ts1, ts2):
    context = StrategyExecutionContext() # Use V2
    result1 = StrategStepEvaluationResult(is_success=True, message="OK1", step_output={"key1": "value1"})
    result2 = StrategStepEvaluationResult(is_success=True, message="OK2", step_output={"key2": "value2"})
    
    key1 = (ts1, step1)
    key2 = (ts2, step2) 

    # Add first result
    context.add_result(ts1, step1, result1)
    assert len(context._strategy_steps_results) == 1 
    assert len(context._latest_results_cache) == 1 
    
    # Add second result
    context.add_result(ts2, step2, result2)

    # Assert final state
    assert len(context._strategy_steps_results) == 2
    assert len(context._latest_results_cache) == 2

    assert key1 in context._strategy_steps_results
    assert key2 in context._strategy_steps_results
    
    assert context._strategy_steps_results[key1] == result1
    assert context._strategy_steps_results[key2] == result2


def test_add_overwriting_result_upon_success(step1, ts1, ts2):
    """Test that adding a new result from the same step overwrites the previous value in cache if the last result was successful."""
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
    assert len(context._strategy_steps_results) == 1
    assert len(context._latest_results_cache) == 1
    assert context._latest_results_cache["trend"] == "UP"  # Check cache after first result
    
    # Add second result from same step
    context.add_result(ts2, step1, result2)
    
    # History should have both results
    assert len(context._strategy_steps_results) == 2
    
    # Cache should still have one entry but with updated value
    assert len(context._latest_results_cache) == 1
    assert context._latest_results_cache["trend"] == "DOWN"  # Check cache after second result
    
    # Both results should be in history
    key1 = (ts1, step1)
    key2 = (ts2, step1)
    assert context._strategy_steps_results[key1] == result1
    assert context._strategy_steps_results[key2] == result2


def test_preserve_successful_result_upon_sebsequent_failure(step1, ts1, ts2):
    """Test that a failed result from the same step does not overwrite a previous successful result in cache."""
    context = StrategyExecutionContext()
    
    # First result from step1 (successful)
    result_success = StrategStepEvaluationResult(
        is_success=True, 
        message="First run successful", 
        step_output={"trend": "UP"}
    )
    
    # Second result from same step (step1) with failure
    result_failure = StrategStepEvaluationResult(
        is_success=False, 
        message="Second run failed", 
        step_output={"trend": "DOWN"}
    )
    
    # Add first result (successful)
    context.add_result(ts1, step1, result_success)
    assert len(context._strategy_steps_results) == 1
    assert len(context._latest_results_cache) == 1
    assert context._latest_results_cache["trend"] == "UP"  # Cache has successful result
    
    # Add second result (failed)
    context.add_result(ts2, step1, result_failure)
    
    # History should have both results
    assert len(context._strategy_steps_results) == 2
    
    # Cache should still have the successful result
    assert len(context._latest_results_cache) == 1
    assert context._latest_results_cache["trend"] == "UP"  # Cache preserves successful result
    
    # Both results should be in history
    key1 = (ts1, step1)
    key2 = (ts2, step1)
    assert context._strategy_steps_results[key1] == result_success
    assert context._strategy_steps_results[key2] == result_failure

    # Assert that the latest successful result is returned through the getter
    latest_result = context.get_latest_strategey_step_output_result("trend")
    assert latest_result == "UP"  # The cache should still hold the successful result


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
    result1 = StrategStepEvaluationResult(
        is_success=True,
        message="Step 1 result",
        step_output=same_output
    )
    
    result2 = StrategStepEvaluationResult(
        is_success=True,
        message="Step 2 result",
        step_output=same_output  # Same output as step1
    )
    
    context = StrategyExecutionContext()
    
    # Add first result successfully
    context.add_result(ts1, step1, result1)
    assert len(context._strategy_steps_results) == 1
    assert len(context._latest_results_cache) == 2  # Two keys in output
    
    # Attempting to add same output from different step should raise ValueError
    with pytest.raises(ValueError, match="cannot produce the same output"):
        context.add_result(ts2, step2, result2)
    
    # Verify context was not modified by the failed call
    assert len(context._strategy_steps_results) == 1
    assert len(context._latest_results_cache) == 2
    assert (ts1, step1) in context._strategy_steps_results
    assert (ts2, step2) not in context._strategy_steps_results

#endregion


@pytest.mark.skip(reason="same as test_reject_duplicate_output_from_different_steps()")
def test_strategy_execution_context_add_result_duplicate_data_v2():
    """Tests that adding a result with duplicate data raises ValueError (V2).
    NOTE: The validation logic in V2 now uses step object equality.
    """
    strategy_step_1 = StrategyStep(
        id="step_dup_1", 
        name="StepDup1",
        description="Test Step Dup 1",
        evaluation_fn=lambda df, ctx, cfg: None,
        config={}
    )
    # Create a step that differs only in name/desc (but same ID) - should NOT cause collision
    strategy_step_1_duplicate = StrategyStep(
        id="step_dup_1", 
        name="StepDup1 Different Name", 
        description="Test Step Dup 1",
        evaluation_fn=lambda df, ctx, cfg: None,
        config={}
    )
    # Create a truly different step
    strategy_step_2 = StrategyStep(
        id="step2",
        name="Step2",
        description="Test Step  2",
        evaluation_fn=lambda df, ctx, cfg: None,
        config={}
    )
    timestamp1 = pd.Timestamp("2023-01-01 10:00:00")
    timestamp2 = pd.Timestamp("2023-01-01 10:05:00")
    timestamp3 = pd.Timestamp("2023-01-01 10:10:00") # For step_diff_name
    step1_payload = {"key1": "value1", "key2": 123}
    dupe_step1_payload = {"key1": "value1", "key2": 123} # Identical payload
    step2_payload = {"keyA": "valueA"} # Different payload

    step1_result = StrategStepEvaluationResult(
        is_success=True, message="Step 1 ok", step_output=step1_payload
    )
    dupe_step1_result = StrategStepEvaluationResult(
        is_success=True, message="Step 2 ok", step_output=dupe_step1_payload  # Same data payload
    )
    step2_result = StrategStepEvaluationResult(
        is_success=True, message="Step 1 diff name ok", step_output=step2_payload
    )

    context = StrategyExecutionContext() # Use V2
    key_step1_original = (timestamp1, strategy_step_1)
    key_step1_duplicate = (timestamp3, strategy_step_1_duplicate)
    key_step2 = (timestamp2, strategy_step_2)

    
    # Add first result successfully
    context.add_result(timestamp1, strategy_step_1, step1_result)
    
    # Add result from step with different name/desc but same ID (should be OK)
    try:
        context.add_result(timestamp3, strategy_step_1_duplicate, step2_result)
    except ValueError as e:
        pytest.fail(f"Adding result from step with different name/desc but same ID raised unexpected ValueError: {e}")
    assert key_step1_duplicate in context._strategy_steps_results # Verify it was added
    assert len(context._strategy_steps_results) == 2

    # Adding the same data payload from a *different* step (different ID) should raise error
    # Match against the error message format which now uses step name/id
    with pytest.raises(ValueError, match=rf"Step '{strategy_step_1.name}' \(ID: {strategy_step_1.id}\)"):
        context.add_result(timestamp2, strategy_step_2, dupe_step1_result)
        
    # Verify context was not modified by the failed call
    assert len(context._strategy_steps_results) == 2 # Still 2 entries
    assert key_step1_original in context._strategy_steps_results
    assert key_step1_duplicate in context._strategy_steps_results
    assert key_step2 not in context._strategy_steps_results # Check the second key wasn't added

# region validation

@pytest.mark.parametrize("test_case", [
    {
        "name": "different_outputs_pass",
        "step1_output": {"key1": "value1"},
        "step2_output": {"key2": "value2"},
        "should_raise": False,
        "error_message": None
    },
    {
        "name": "identical_outputs_fail",
        "step1_output": {"key": "value"},
        "step2_output": {"key": "value"},
        "should_raise": True,
        "error_message": "produced identical output"
    },
    {
        "name": "identical_outputs_different_order_fail",
        "step1_output": {"key1": "value1", "key2": "value2"},
        "step2_output": {"key2": "value2", "key1": "value1"},
        "should_raise": True,
        "error_message": "produced identical output"
    },
    {
        "name": "identical_outputs_nested_dict_fail",
        "step1_output": {"key": {"nested": "value"}},
        "step2_output": {"key": {"nested": "value"}},
        "should_raise": True,
        "error_message": "produced identical output"
    },
    {
        "name": "different_nested_dicts_pass",
        "step1_output": {"key": {"nested1": "value1"}},
        "step2_output": {"key": {"nested2": "value2"}},
        "should_raise": False,
        "error_message": None
    },
    {
        "name": "different_nested_lists_pass",
        "step1_output": {"key": [1, 2, 3]},
        "step2_output": {"key": [4, 5, 6]},
        "should_raise": False,
        "error_message": None
    },
    {
        "name": "different_nested_mixed_pass",
        "step1_output": {"key": {"nested": [1, 2, 3]}},
        "step2_output": {"key": {"nested": [4, 5, 6]}},
        "should_raise": False,
        "error_message": None
    },
    {
        "name": "different_nested_structure_pass",
        "step1_output": {"key": {"nested": "value"}},
        "step2_output": {"key": ["value"]},
        "should_raise": False,
        "error_message": None
    },
    {
        "name": "identical_outputs_list_fail",
        "step1_output": {"key": [1, 2, 3]},
        "step2_output": {"key": [1, 2, 3]},
        "should_raise": True,
        "error_message": "produced identical output"
    },
    {
        "name": "identical_outputs_mixed_types_fail",
        "step1_output": {"key1": 123, "key2": "value", "key3": True},
        "step2_output": {"key1": 123, "key2": "value", "key3": True},
        "should_raise": True,
        "error_message": "produced identical output"
    },
    {
        "name": "empty_outputs_pass",
        "step1_output": {}, # empty dict is outside of this validation logic
        "step2_output": {"key": "value"},
        "should_raise": False,
        "error_message": None
    },
    {
        "name": "none_outputs_pass",
        "step1_output": None,
        "step2_output": {"key": "value"},
        "should_raise": False,
        "error_message": None
    },
    {
        "name": "partial_match_pass",
        "step1_output": {"key1": "value1", "key2": "value2"},
        "step2_output": {"key1": "value1", "key3": "value3"},
        "should_raise": False,
        "error_message": None
    }
])
def test_validate_step_outputs_for_duplicate_results(test_case):
    """Test validation of step outputs with different scenarios."""
    context = StrategyExecutionContext()
    
    # Create two different steps
    step1 = StrategyStep(
        id="step1",
        name="Step 1",
        evaluation_fn=lambda x, y, z: None
    )
    
    step2 = StrategyStep(
        id="step2",
        name="Step 2",
        evaluation_fn=lambda x, y, z: None
    )
    
    # Create results with specified outputs
    result1 = StrategStepEvaluationResult(
        is_success=True,
        step_output=test_case["step1_output"]
    )
    
    result2 = StrategStepEvaluationResult(
        is_success=True,
        step_output=test_case["step2_output"]
    )
    
    # Test validation
    if test_case["should_raise"]:
        with pytest.raises(ValueError) as exc_info:
            context._validate_no_duplicate_outputs_by_different_steps(
                step1,
                result1,
                {(None, step2): result2}
            )
        if test_case["error_message"]:
            assert test_case["error_message"] in str(exc_info.value)
            assert "Step 1" in str(exc_info.value)
            assert "Step 2" in str(exc_info.value)
    else:
        # This should not raise an exception
        context._validate_no_duplicate_outputs_by_different_steps(
            step1,
            result1,
            {(None, step2): result2}
        )


@pytest.mark.parametrize("test_case", [
    {
        "name": "valid_outputs_pass",
        "step_output": {"key1": "value1", "key2": 123, "key3": True},
        "should_raise": False,
        "error_message": None
    },
    {
        "name": "empty_key_fails",
        "step_output": {"": "value1"},
        "should_raise": True,
        "error_message": "produced output with empty key"
    },
    {
        "name": "whitespace_key_fails",
        "step_output": {"   ": "value1"},
        "should_raise": True,
        "error_message": "produced output with empty key"
    },
    {
        "name": "none_value_fails",
        "step_output": {"key1": None},
        "should_raise": True,
        "error_message": "produced output with empty value for key 'key1'"
    },
    {
        "name": "empty_string_value_fails",
        "step_output": {"key1": ""},
        "should_raise": True,
        "error_message": "produced output with empty value for key 'key1'"
    },
    {
        "name": "whitespace_string_value_fails",
        "step_output": {"key1": "   "},
        "should_raise": True,
        "error_message": "produced output with empty value for key 'key1'"
    },
    {
        "name": "none_output_pass",
        "step_output": None,
        "should_raise": False,
        "error_message": None
    },
    {
        "name": "empty_dict_output_pass",
        "step_output": {},
        "should_raise": False,
        "error_message": None
    }
])
def test_validate_step_output_keys_and_values(test_case):
    """Test validation of step output keys and values with different scenarios."""
    context = StrategyExecutionContext()
    
    # Create a test step
    step = StrategyStep(
        id="test_step",
        name="Test Step",
        evaluation_fn=lambda x, y, z: None
    )
    
    # Create result with specified output
    result = StrategStepEvaluationResult(
        is_success=True,
        step_output=test_case["step_output"]
    )
    
    # Test validation
    if test_case["should_raise"]:
        with pytest.raises(ValueError) as exc_info:
            context._validate_step_output_keys_and_values(step, result)
        if test_case["error_message"]:
            assert test_case["error_message"] in str(exc_info.value)
            assert "Test Step" in str(exc_info.value)
    else:
        # This should not raise an exception
        context._validate_step_output_keys_and_values(step, result)

#endregion


