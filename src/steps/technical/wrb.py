"""Identifies if the current bar or series of directional bars as wide range bar or gap bar

"""

from typing import Any, Dict, Tuple

import pandas as pd

from src.models.base import PriceLabel
from src.models.strategy import StrategStepEvaluationResult, StrategyExecutionContext
from src.utils import create_failure_result, create_success_result


def _validate_lookup_bars(
    data: pd.DataFrame,
    lookback_bars: int
) -> bool:
    """Validate if there are enough bars for the lookback period.
    
    Args:
        data: Price data to analyze
        lookback_bars: Number of bars to look back
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValueError: If data is empty or insufficient bars for lookback period
    """
    if data.empty:
        raise ValueError("No data available")
    
    if len(data) < lookback_bars:
        raise ValueError(f"Not enough bars for lookback period. Required: {lookback_bars}, Available: {len(data)}")
    
    return True


def _get_bar_high_low_range(
    price_data: pd.DataFrame,
    index: pd.Timestamp
) -> float:
    """Calculate the high-low range of a single bar by datetime index.
    
    Args:
        price_data: Price data
        index: Datetime index label of the bar to measure
        
    Returns:
        Size of the bar (high - low)
        
    Raises:
        KeyError: If index is not in the DataFrame index or required price columns are missing
    """
    bar = price_data.loc[index]
    return bar[PriceLabel.HIGH] - bar[PriceLabel.LOW]


def _is_bar_wider_than_lookback(
    price_data: pd.DataFrame,
    current_bar_index: pd.Timestamp,
    lookback_bars: int,
    min_size_increase_pct: float
) -> Tuple[bool, float]:
    """Check if current bar is wider than any bar in lookback period.
    
    Args:
        price_data: Price data
        current_bar_index: Datetime index of the current bar
        lookback_bars: Number of bars to look back
        min_size_increase_pct: Minimum percentage increase required
        
    Returns:
        Tuple of (is_wider, size_increase_pct)
        
    Raises:
        IndexError: If current_bar_index or lookback range is out of bounds
        KeyError: If required price columns are missing
        ZeroDivisionError: If average lookback size is zero
    """
    current_bar_size = _get_bar_high_low_range(price_data, current_bar_index)
    
    # Get indices of lookback bars
    current_idx = price_data.index.get_loc(current_bar_index)
    lookback_indices = price_data.index[current_idx - lookback_bars:current_idx]
    
    if len(lookback_indices) == 0:
        return False, 0.0
    
    # Get sizes of lookback bars
    lookback_sizes = [
        _get_bar_high_low_range(price_data, idx)
        for idx in lookback_indices
    ]
    
    # Calculate average size of lookback bars
    avg_lookback_size = sum(lookback_sizes) / len(lookback_sizes)
    
    if avg_lookback_size == 0:
        raise ZeroDivisionError("Average lookback bar size is zero")
    
    # Calculate size increase percentage
    size_increase_pct = ((current_bar_size - avg_lookback_size) / avg_lookback_size) * 100
    
    return size_increase_pct >= min_size_increase_pct, size_increase_pct


def detect_wide_range_bar(
    price_data: pd.DataFrame,
    context: StrategyExecutionContext,
    config: Dict[str, Any]
) -> StrategStepEvaluationResult:
    """Detect if the latest bar is significantly wider than recent bars.
    
    Args:
        price_data: Price data to analyze
        context: Current strategy execution context
        config: Configuration parameters including:
            - lookback_bars: Number of bars to look back (default: 20)
            - min_size_increase_pct: Minimum percentage increase required (default: 50.0)
            
    Returns:
        Result containing wide range bar detection information:
        - is_wide_range: Whether the current bar is a wide range bar
        - size_increase_pct: Percentage increase in size compared to average
        - lookback_bars: Number of bars used for comparison
        - min_size_increase_pct: Minimum percentage increase required
    """
    lookback_bars = config.get('lookback_bars', 20)
    min_size_increase_pct = config.get('min_size_increase_pct', 50.0)
    
    try:
        # Validate input
        _validate_lookup_bars(price_data, lookback_bars)
        
        # Check if current bar is wider
        is_wider, size_increase = _is_bar_wider_than_lookback(
            price_data,
            price_data.index[-1],  # Latest bar
            lookback_bars,
            min_size_increase_pct
        )
        
        return create_success_result(
            data=price_data,
            step=context.current_step,
            step_output={
                'is_wide_range': is_wider,
                'size_increase_pct': size_increase,
                'lookback_bars': lookback_bars,
                'min_size_increase_pct': min_size_increase_pct
            }
        )
    except ValueError as e:
        return create_failure_result(
            data=price_data,
            step=context.current_step,
            error_msg=str(e)
        )
    except (IndexError, KeyError) as e:
        return create_failure_result(
            data=price_data,
            step=context.current_step,
            error_msg="Invalid price data format or index",
            e=e
        )
    except ZeroDivisionError as e:
        return create_failure_result(
            data=price_data,
            step=context.current_step,
            error_msg="Cannot calculate size increase: average bar size is zero",
            e=e
        )
    except Exception as e:
        return create_failure_result(
            data=price_data,
            step=context.current_step,
            error_msg="Error detecting wide range bar",
            e=e
        ) 