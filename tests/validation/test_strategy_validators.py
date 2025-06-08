import pytest

from src.models.strategy import StrategyStep, StrategyStepEvaluationResult
from src.validation.validators import (
    validate_no_duplicate_outputs_by_different_steps,
    validate_step_output_keys_and_values,
)


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
    },
    {
        "name": "same_step_same_output_pass",
        "step1_output": {"key": "value"},
        "step2_output": {"key": "value"},
        "same_step": True,
        "should_raise": True,
        "error_message": None
    }
])
def test_validate_step_outputs_for_duplicate_results(test_case):
    """Test validation of step outputs with different scenarios."""
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
    result1 = StrategyStepEvaluationResult(
        is_success=True,
        step_output=test_case["step1_output"]
    )
    
    result2 = StrategyStepEvaluationResult(
        is_success=True,
        step_output=test_case["step2_output"]
    )
    
    # Test validation
    if test_case["should_raise"]:
        with pytest.raises(ValueError) as exc_info:
            validate_no_duplicate_outputs_by_different_steps(
                cur_step=step1,
                cur_step_result=result1,
                prev_results={(None, step2): result2}
            )
        if test_case["error_message"]:
            assert test_case["error_message"] in str(exc_info.value)
            assert "Step 1" in str(exc_info.value)
            assert "Step 2" in str(exc_info.value)
    else:
        # This should not raise an exception
        validate_no_duplicate_outputs_by_different_steps(
            cur_step=step1,
            cur_step_result=result1,
            prev_results={(None, step2): result2}
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
    # Create a test step
    step = StrategyStep(
        id="test_step",
        name="Test Step",
        evaluation_fn=lambda x, y, z: None
    )
    
    # Create result with specified output
    result = StrategyStepEvaluationResult(
        is_success=True,
        step_output=test_case["step_output"]
    )
    
    # Test validation
    if test_case["should_raise"]:
        with pytest.raises(ValueError) as exc_info:
            validate_step_output_keys_and_values(step, result)
        if test_case["error_message"]:
            assert test_case["error_message"] in str(exc_info.value)
            assert "Test Step" in str(exc_info.value)
    else:
        # This should not raise an exception
        validate_step_output_keys_and_values(step, result)


def test_validate_identical_output_by_different_steps():
    """Test that _validate_identical_output_by_different_steps correctly prevents different steps from producing identical outputs."""
    # Create two different steps
    step1 = StrategyStep(
        id="step1",
        name="Step One",
        evaluation_fn=lambda x, y, z: None
    )
    
    step2 = StrategyStep(
        id="step2",
        name="Step Two",
        evaluation_fn=lambda x, y, z: None
    )
    
    # Create a result with some output
    result = StrategyStepEvaluationResult(
        is_success=True,
        step_output={"key": "value"}
    )
    
    # First step adds output successfully
    with pytest.raises(ValueError) as exc_info:
        validate_no_duplicate_outputs_by_different_steps(
            cur_step=step1,
            cur_step_result=result,
            prev_results={(None, step2): result}
        )
    
    # Verify error message
    assert str(exc_info.value) == "Steps 'Step One' and 'Step Two' produced identical output: ['key']. Two StrategySteps cannot produce the same output." 