# tests/mocks/mock_step_functions.py

from typing import Any, Dict

import pandas as pd

# Update imports from src

# Import the "pure" mock functions to be wrapped
# Use relative import as it's now in the same directory

# --- Agreed upon Data Keys ---
EXTREME_BAR_INDEX_KEY = "extreme_bar_index"


# --- Helper to get latest timestamp safely ---
def _get_latest_timestamp(price_feed: pd.DataFrame) -> pd.Timestamp:
    if price_feed.empty or not isinstance(price_feed.index, pd.DatetimeIndex) or len(price_feed.index) == 0:
        # Raise ValueError if price_feed is invalid
        raise ValueError("Price feed is empty or has an invalid index, cannot determine latest timestamp.")
    return price_feed.index[-1]

# --- Mock Wrapper Functions ---


def mock_detect_trend_wrapper(price_feed: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """Mock trend detection wrapper."""
    return {"trend": "UP"}


def mock_find_extreme_wrapper(price_feed: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """Mock extreme bar detection wrapper."""
    return {"is_extreme": True, "extreme_bar_index": price_feed.index[-1]}


def mock_validate_pullback_wrapper(price_feed: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """Mock pullback validation wrapper."""
    return {"bars_valid": True}


def mock_check_fib_wrapper(price_feed: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """Mock Fibonacci check wrapper."""
    return {"fib_valid": True} 