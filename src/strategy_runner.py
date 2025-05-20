"""Contains functions for executing a defined strategy step-by-step."""

from typing import Optional

import pandas as pd

# Import necessary types from models using absolute path from src
from src.models import (
    StrategStepEvaluationResult,
    StrategyConfig,
    StrategyExecutionContext,
    StrategyStep,
)


def _execute_strategy_step(
    step: StrategyStep, 
    price_feed: pd.DataFrame, 
    context: StrategyExecutionContext
) -> StrategStepEvaluationResult:
    """Executes a single strategy step using the provided context."""
    # print(f"    Context Before Keys: {str(context)}")
    try:
        # Expected wrapper signature: 
        # (price_feed: pd.DataFrame, context: ?, **config) -> StrategStepEvaluationResult
        # The evaluation function itself might expect a specific context version.
        result : StrategStepEvaluationResult = step.evaluation_fn(
            price_feed=price_feed,
            context=context,
            **step.config
        )
    except Exception as e:
        # Catch errors during the wrapper execution itself
        return StrategStepEvaluationResult(is_success=False, message=f"Error executing step '{step.name}' wrapper: {e}")

    # Guard: Ensure the wrapper returned the correct type 
       
    if not isinstance(result, StrategStepEvaluationResult):
        return StrategStepEvaluationResult(
            is_success=False, 
            message=f"Step '{step.name}' evaluation function returned {type(result).__name__}, expected StrategStepEvaluationResult"
        )
    return result


def run_strategy(
    strategy: StrategyConfig,
    price_feed: pd.DataFrame,
    context: Optional[StrategyExecutionContext] = None
) -> StrategyExecutionContext:
    """Executes strategy steps using a persistent context, updated per call.

    This version is intended to be called repeatedly (e.g., per new price bar),
    passing the context from the previous call to maintain state.

    Args:
        strategy: The strategy configuration containing the steps.
        price_feed: The DataFrame of price data (potentially growing over time).
        context: The StrategyExecutionContext from the *previous* execution.

    Returns:
        The updated StrategyExecutionContext after processing the steps for this call.
        Stops processing steps for this call upon the first failure or validation error.
    """
    print(f"Running strategy: {strategy.name} with existing bar index {price_feed.index[-1]}")

    if context is None:
        context = StrategyExecutionContext()

    # Check if price_feed is empty or has no valid index
    if price_feed.empty or not isinstance(price_feed.index, pd.DatetimeIndex) or len(price_feed.index) == 0:
        print("  Warning: Price feed is empty or has no valid index. Skipping execution for this call.")
        # Decide on behavior: return existing context or raise error?
        # Returning existing context seems safer for repeated calls.
        return context 

    # Get the index of the latest bar *safely*
    latest_bar_index = price_feed.index[-1]

    for i in range(1, len(price_feed) + 1):  # start at 1, include last bar
        incremental_price_feed = price_feed.iloc[:i]  # Now first slice will have one row
        print(f"  Executing step {i}: {strategy.steps[i-1].name} (ID: {strategy.steps[i-1].id}) using context")
        
        # Execute step with the context as it is *at the start of this call*
        result: StrategStepEvaluationResult = _execute_strategy_step(strategy.steps[i-1], incremental_price_feed, context=context)

        # Add result to context using the latest bar's index
        try:
            context.add_result(latest_bar_index, strategy.steps[i-1], result)
        except ValueError as ve: # Catch potential validation errors from add_result
            print(f"  Validation Error during add_result for step '{strategy.steps[i-1].name}': {ve}")
            print("  Stopping step processing for this call due to validation error.")
            break # Stop processing further steps for this call
        
        if result.is_success:
            print(f"    Success: {result.message or ''} {result.step_output or ''}")
        else:
            print(f"    Failed: {result.message or 'No message'}")
            print("  Stopping step processing for this call due to step failure.")
            break # Stop processing further steps *for this specific call* 
            
    print(f"Strategy {strategy.name} execution finished for this bar, {latest_bar_index}")
    return context 