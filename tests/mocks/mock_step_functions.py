# tests/mocks/mock_step_functions.py

from typing import Any, Dict

import pandas as pd

# Update imports from src
from src.models import StrategStepEvaluationResult, StrategyExecutionContext

# Import the "pure" mock functions to be wrapped
# Use relative import as it's now in the same directory
from .mock_pure_logic import (
    mock_pure_get_trend,
    mock_pure_is_bars_since_extreme_pivot_valid,
    mock_pure_is_extreme_bar,
    mock_pure_is_within_fib_extension,
)

# from src.strategy import StrategyExecutionContext # Remove old import


# --- Agreed upon Data Keys ---
EXTREME_BAR_INDEX_KEY = "extreme_bar_index_data"

# --- Mock Wrapper Functions ---


def mock_detect_trend_wrapper(
    price_feed: pd.DataFrame, 
    context: StrategyExecutionContext, # Uses imported type
    **config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Wrapper for mock_pure_get_trend."""
    try:
        result_data = mock_pure_get_trend(price_feed, **config)
        return StrategStepEvaluationResult(success=True, message="Trend detected", data=result_data)
    except Exception as e:
        return StrategStepEvaluationResult(success=False, message=f"Error in mock_detect_trend_wrapper: {e}")


def mock_find_extreme_wrapper(
    price_feed: pd.DataFrame, 
    context: StrategyExecutionContext, # Uses imported type
    **config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Wrapper for mock_pure_is_extreme_bar. Outputs extreme_bar_index_data."""
    frame_size = config.get("frame_size")
    if frame_size is None:
        return StrategStepEvaluationResult(success=False, message="Missing 'frame_size' in config")
    try:
        result_data = mock_pure_is_extreme_bar(price_feed, frame_size=frame_size)
        # Prepare output data with the agreed key
        output_data = {EXTREME_BAR_INDEX_KEY: result_data.get("extreme_bar_index"), "is_extreme": result_data.get("is_extreme")}
        return StrategStepEvaluationResult(
            success=True, 
            message="Extreme bar found", 
            data=output_data
        )
    except Exception as e:
        return StrategStepEvaluationResult(success=False, message=f"Error in mock_find_extreme_wrapper: {e}")


def mock_validate_pullback_wrapper(
    price_feed: pd.DataFrame, 
    context: StrategyExecutionContext, # Uses imported type
    **config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Wrapper for mock_pure_is_bars_since_extreme_pivot_valid. Needs EXTREME_BAR_INDEX_KEY."""
    lookup = context.find_latest_successful_data(EXTREME_BAR_INDEX_KEY)
    if lookup is None:
        return StrategStepEvaluationResult(success=False, message=f"Required data key '{EXTREME_BAR_INDEX_KEY}' not found in context")
    
    # Assuming find_latest_successful_data returns just the value based on previous edits
    extreme_bar_index = lookup 
    # producing_step_id, extreme_bar_index = lookup # Old assumption
    # print(f"    Wrapper received: {extreme_bar_index=} from step {producing_step_id}") # Old print
    print(f"    Wrapper received: {extreme_bar_index=}") # Updated print

    if extreme_bar_index is None:
         return StrategStepEvaluationResult(success=False, message=f"Value for '{EXTREME_BAR_INDEX_KEY}' was None")

    min_bars = config.get("min_bars")
    max_bars = config.get("max_bars")
    if min_bars is None or max_bars is None:
         return StrategStepEvaluationResult(success=False, message="Missing 'min_bars' or 'max_bars' in config")

    try:
        result_data = mock_pure_is_bars_since_extreme_pivot_valid(
            price_feed=price_feed, 
            extreme_bar_index=extreme_bar_index, 
            min_bars=min_bars, 
            max_bars=max_bars
        )
        return StrategStepEvaluationResult(success=True, message="Pullback valid", data=result_data)
    except Exception as e:
        return StrategStepEvaluationResult(success=False, message=f"Error in mock_validate_pullback_wrapper: {e}")


def mock_check_fib_wrapper(
    price_feed: pd.DataFrame, 
    context: StrategyExecutionContext, # Uses imported type
    **config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Wrapper for mock_pure_is_within_fib_extension."""
    min_ext = config.get("min_extension")
    max_ext = config.get("max_extension")
    if min_ext is None or max_ext is None:
         return StrategStepEvaluationResult(success=False, message="Missing 'min_extension' or 'max_extension' in config")

    try:
        result_data = mock_pure_is_within_fib_extension(
            price_feed=price_feed, 
            min_extension=min_ext, 
            max_extension=max_ext
        )
        return StrategStepEvaluationResult(success=True, message="Fib valid", data=result_data)
    except Exception as e:
        return StrategStepEvaluationResult(success=False, message=f"Error in mock_check_fib_wrapper: {e}") 