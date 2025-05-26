"""Identifies if the current bar or series of directional bars as wide range bar or gap bar

"""

from typing import Any, Dict, Tuple

import pandas as pd

from src.models.strategy import (
    StrategStepEvaluationResult,
    StrategyExecutionContext,
)
from src.utils import create_failure_result, create_success_result


def _validate_lookup_bars(
    data: pd.DataFrame,
    lookback_bars: int
) -> Tuple[bool, str]:
    """Validate if there are enough bars for the lookback period.
    
    Args:
        data: Price data to analyze
        lookback_bars: Number of bars to look back
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if data.empty:
        return False, "No data available"
    
    if len(data) < lookback_bars:
        return False, f"Not enough bars for lookback period. Required: {lookback_bars}, Available: {len(data)}"
    
    return True, ""


def _get_bar_size(
    data: pd.DataFrame,
    bar_index: int
) -> float:
    """Calculate the size of a single bar.
    
    Args:
        data: Price data
        bar_index: Index of the bar to measure
        
    Returns:
        Size of the bar (high - low)
    """
    bar = data.iloc[bar_index]
    return bar['high'] - bar['low']


def _is_bar_wider_than_lookback(
    data: pd.DataFrame,
    current_bar_index: int,
    lookback_bars: int,
    min_size_increase_pct: float
) -> Tuple[bool, float]:
    """Check if current bar is wider than any bar in lookback period.
    
    Args:
        data: Price data
        current_bar_index: Index of the current bar
        lookback_bars: Number of bars to look back
        min_size_increase_pct: Minimum percentage increase required
        
    Returns:
        Tuple of (is_wider, size_increase_pct)
    """
    current_bar_size = _get_bar_size(data, current_bar_index)
    
    # Get sizes of lookback bars
    lookback_sizes = [
        _get_bar_size(data, i)
        for i in range(current_bar_index - lookback_bars, current_bar_index)
    ]
    
    if not lookback_sizes:
        return False, 0.0
    
    # Calculate average size of lookback bars
    avg_lookback_size = sum(lookback_sizes) / len(lookback_sizes)
    
    # Calculate size increase percentage
    size_increase_pct = ((current_bar_size - avg_lookback_size) / avg_lookback_size) * 100
    
    return size_increase_pct >= min_size_increase_pct, size_increase_pct


def detect_wide_range_bar(
    data: pd.DataFrame,
    context: StrategyExecutionContext,
    config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Detect if the latest bar is significantly wider than recent bars.
    
    Args:
        data: Price data to analyze
        context: Current strategy execution context
        config: Configuration parameters including:
            - lookback_bars: Number of bars to look back
            - min_size_increase_pct: Minimum percentage increase required
            
    Returns:
        Result containing wide range bar detection information
    """
    lookback_bars = config.get('lookback_bars', 20)
    min_size_increase_pct = config.get('min_size_increase_pct', 50.0)
    
    # Validate input
    is_valid, error_msg = _validate_lookup_bars(data, lookback_bars)
    if not is_valid:
        return create_failure_result(
            data=data,
            step=context.current_step,
            error_msg=error_msg
        )
    
    try:
        # Check if current bar is wider
        is_wider, size_increase = _is_bar_wider_than_lookback(
            data,
            -1,  # Latest bar
            lookback_bars,
            min_size_increase_pct
        )
        
        return create_success_result(
            data=data,
            step=context.current_step,
            step_output={
                'is_wide_range': is_wider,
                'size_increase_pct': size_increase,
                'lookback_bars': lookback_bars,
                'min_size_increase_pct': min_size_increase_pct
            }
        )
    except Exception as e:
        return create_failure_result(
            data=data,
            step=context.current_step,
            error_msg="Error detecting wide range bar",
            e=e
        ) 