"""Validation functions for strategy execution."""

from typing import TYPE_CHECKING, Dict

import pandas as pd

if TYPE_CHECKING:
    from src.models.strategy import StrategyStep, StrategyStepEvaluationResult


def validate_step_output_keys_and_values(
    step: 'StrategyStep',
    result: 'StrategyStepEvaluationResult'
) -> None:
    """Validate that step output keys and values are non-empty.
    
    Args:
        step: The strategy step being validated
        result: The result containing the output to validate
        
    Raises:
        ValueError: If any key or value in the output is empty
    """
    if not result.step_output:
        return
        
    for key, value in result.step_output.items():
        if not key or not key.strip():
            raise ValueError(f"Step '{step.name}' produced output with empty key")
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"Step '{step.name}' produced output with empty value for key '{key}'")


def validate_no_duplicate_outputs_by_different_steps(
    cur_step: 'StrategyStep',
    cur_step_result: 'StrategyStepEvaluationResult',
    prev_results: Dict[tuple[pd.Timestamp, 'StrategyStep'], 'StrategyStepEvaluationResult']
) -> None:
    """Ensure only one step produces a given output.

    Args:
        cur_step: The current step being validated
        cur_step_result: The result from the current step
        prev_results: Previous results to check against

    Raises:
        ValueError: If another step has already produced the same output
    """
    if not cur_step_result.step_output:
        return
        
    for (_, existing_step), existing_result in prev_results.items():
        if (existing_step != cur_step 
            and existing_result.step_output 
            and existing_result.step_output == cur_step_result.step_output):
            raise ValueError(
                f"Steps '{cur_step.system_step_id}' and '{existing_step.system_step_id}' "
                f"produced identical output: {list(cur_step_result.step_output.keys())}. "
                "Two StrategySteps cannot produce the same output."
            )


def validate_identical_output_by_different_steps(
    cur_step: 'StrategyStep',
    cur_step_result: 'StrategyStepEvaluationResult',
    prev_results: Dict[tuple[pd.Timestamp, 'StrategyStep'], 'StrategyStepEvaluationResult']
) -> None:
    """Ensure that different StrategySteps do not produce identical output keys.

    If two different steps produce the same output key, it indicates a bug - error out.

    Args:
        cur_step: The current step being validated
        cur_step_result: The result from the current step
        prev_results: Previous results to check against

    Raises:
        ValueError: If another step has already produced the same output key
    """
    if not cur_step_result.step_output:
        return
        
    for (_, existing_step), existing_result in prev_results.items():
        if (existing_step != cur_step 
            and existing_result.step_output):
            # Check for any overlapping keys
            overlapping_keys = set(cur_step_result.step_output.keys()) & set(existing_result.step_output.keys())
            if overlapping_keys:
                raise ValueError(
                    f"Steps '{cur_step.system_step_id}' and '{existing_step.system_step_id}' "
                    f"produced identical output keys: {list(overlapping_keys)}. "
                    "Two different StrategySteps cannot produce the same output key."
                )
