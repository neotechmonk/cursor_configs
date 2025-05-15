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

# --- Agreed upon Data Keys ---
EXTREME_BAR_INDEX_KEY = "extreme_bar_index"


# --- Helper to get latest timestamp safely ---
def _get_latest_timestamp(price_feed: pd.DataFrame) -> pd.Timestamp:
    if price_feed.empty or not isinstance(price_feed.index, pd.DatetimeIndex) or len(price_feed.index) == 0:
        # Raise ValueError if price_feed is invalid
        raise ValueError("Price feed is empty or has an invalid index, cannot determine latest timestamp.")
    return price_feed.index[-1]

# --- Mock Wrapper Functions ---


def mock_detect_trend_wrapper(
    price_feed: pd.DataFrame, 
    context: StrategyExecutionContext,
    **config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Wrapper for mock_pure_get_trend."""
    latest_timestamp = _get_latest_timestamp(price_feed)
    try:
        result_data = mock_pure_get_trend(price_feed, **config)
        return StrategStepEvaluationResult(is_success=True, message="Trend detected", step_output=result_data, timestamp=latest_timestamp)
    except Exception as e:
        return StrategStepEvaluationResult(is_success=False, message=f"Error in mock_detect_trend_wrapper: {e}", timestamp=latest_timestamp)


def mock_find_extreme_wrapper(
    price_feed: pd.DataFrame, 
    context: StrategyExecutionContext,
    **config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Wrapper for mock_pure_is_extreme_bar."""
    latest_timestamp = _get_latest_timestamp(price_feed)
    try:
        result_data = mock_pure_is_extreme_bar(price_feed, **config)
        return StrategStepEvaluationResult(
            is_success=True, 
            message="Extreme bar detected", 
            step_output=result_data, 
            timestamp=latest_timestamp
        )
    except Exception as e:
        return StrategStepEvaluationResult(is_success=False, message=f"Error in mock_find_extreme_wrapper: {e}", timestamp=latest_timestamp)


def mock_validate_pullback_wrapper(
    price_feed: pd.DataFrame, 
    context: StrategyExecutionContext,
    **config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Wrapper for mock_pure_is_bars_since_extreme_pivot_valid."""
    latest_timestamp = _get_latest_timestamp(price_feed)

    extreme_bar_index = context.find_latest_successful_data(EXTREME_BAR_INDEX_KEY)
    try:
        result_data = mock_pure_is_bars_since_extreme_pivot_valid(price_feed=price_feed, extreme_bar_index = extreme_bar_index, **config)
        return StrategStepEvaluationResult(
            is_success=True, 
            message="Pullback valid", 
            step_output={'bars_valid': True}, # TODO: Fix manually overriden payload
            timestamp=latest_timestamp
        )
    except Exception as e:
        return StrategStepEvaluationResult(is_success=False, message=f"Error in mock_validate_pullback_wrapper: {e}", timestamp=latest_timestamp)


def mock_check_fib_wrapper(
    price_feed: pd.DataFrame, 
    context: StrategyExecutionContext,
    **config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Wrapper for mock_pure_is_within_fib_extension."""
    latest_timestamp = _get_latest_timestamp(price_feed)
    try:
        result_data = mock_pure_is_within_fib_extension(price_feed, **config)
        return StrategStepEvaluationResult(
            is_success=True, 
            message="Fib valid", 
            step_output=result_data, 
            timestamp=latest_timestamp
        )
    except Exception as e:
        return StrategStepEvaluationResult(is_success=False, message=f"Error in mock_check_fib_wrapper: {e}", timestamp=latest_timestamp) 