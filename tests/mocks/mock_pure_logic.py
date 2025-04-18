"""Pure mock functions representing strategy logic components,
   intended to be called by wrapper functions.
"""

from typing import Any, Dict

import pandas as pd


def mock_pure_get_trend(price_feed: pd.DataFrame, **config: Dict[str, Any]) -> Dict[str, Any]:
    """Pure mock: Returns trend data."""
    # Simulate some logic
    return {"trend": "UP"}


def mock_pure_is_extreme_bar(price_feed: pd.DataFrame, frame_size: int) -> Dict[str, Any]:
    """Pure mock: Returns extreme bar check data."""
    # Simulate logic using frame_size
    # Ensure price_feed is not empty
    if price_feed.empty:
        return {"is_extreme": False, "extreme_bar_index": None}
    return {"is_extreme": True, "extreme_bar_index": price_feed.index[-1]} # Example: output index


def mock_pure_is_bars_since_extreme_pivot_valid(
    price_feed: pd.DataFrame, 
    extreme_bar_index: pd.Timestamp, # Expects index from previous step
    min_bars: int, 
    max_bars: int
) -> Dict[str, Any]:
    """Pure mock: Returns pullback validity data."""
    # Simulate logic using extreme_bar_index, min_bars, max_bars
    print(f"    Pure func received: {extreme_bar_index=}") # Debug print
    # Add basic check for valid index
    if extreme_bar_index is None or extreme_bar_index not in price_feed.index:
        return {"bars_valid": False} 
        
    # Example logic
    bars_since = len(price_feed[price_feed.index > extreme_bar_index]) 
    is_valid = min_bars <= bars_since <= max_bars
    return {"bars_valid": is_valid}


def mock_pure_is_within_fib_extension(
    price_feed: pd.DataFrame, 
    min_extension: float, 
    max_extension: float
) -> Dict[str, Any]:
    """Pure mock: Returns Fib extension validity data."""
    # Simulate logic using min_extension, max_extension
    # (Add basic checks if needed)
    return {"fib_valid": True} 