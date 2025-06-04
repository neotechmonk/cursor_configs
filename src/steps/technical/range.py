"""Identifies if the current bar or series of directional bars as wide range bar or gap bar

"""

from typing import Any, Dict, Literal

import pandas as pd

from src.models.base import PriceLabel
from src.models.strategy import StrategStepEvaluationResult, StrategyExecutionContext
from src.utils import create_failure_result, create_success_result

# Type alias for comparison methods
ComparisonMethod = Literal["max", "avg"]


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
        
    Raises:
        IndexError: If bar_index is out of bounds
        KeyError: If required price columns are missing
    """
    bar = data.iloc[bar_index]
    return bar[PriceLabel.HIGH] - bar[PriceLabel.LOW]


def _get_wrb_series_range(
    data: pd.DataFrame,
    current_bar_index: pd.Timestamp,
) -> tuple[float, list[pd.Timestamp]]:
    """Calculate the range of a wide range bar series in a trend.
    
    A wide range bar series is defined as consecutive bars where either:
    For uptrend:
    1. Each bar's high is higher than the previous bar's high
    2. The close of the current bar is higher than the previous high
    
    OR for downtrend:
    1. Each bar's low is lower than the previous bar's low
    2. The close of the current bar is lower than the previous low
    
    Args:
        data: Price data
        current_bar_index: Datetime index of the current bar
        
    Returns:
        tuple[float, list[pd.Timestamp]]: (high-low range of the series, list of indices in the series)
        
    Raises:
        IndexError: If current_bar_index is not in the DataFrame index
        KeyError: If required price columns are missing
    """
    try:
        current_idx = data.index.get_loc(current_bar_index)
    except KeyError:
        raise IndexError(f"Current bar index {current_bar_index} not found in data")
    
    wrb_series_indices = [data.index[current_idx]]
    for i in range(current_idx, 0, -1):
        curr_bar = data.iloc[i]
        prev_bar = data.iloc[i-1]
        prev_idx = data.index[i-1]
        
        # Define trend conditions using all() for consistency
        # m
        is_uptrend_qualified_wrb = all([
            curr_bar[PriceLabel.HIGH] > prev_bar[PriceLabel.HIGH],
            curr_bar[PriceLabel.CLOSE] >= prev_bar[PriceLabel.HIGH]
        ])
        
        is_downtrend_qualified_wrb = all([
            curr_bar[PriceLabel.LOW] < prev_bar[PriceLabel.LOW],
            curr_bar[PriceLabel.CLOSE] <= prev_bar[PriceLabel.LOW]
        ])
        
        if is_uptrend_qualified_wrb or is_downtrend_qualified_wrb:
            wrb_series_indices.append(prev_idx)
        else:
            break
                
    series_bars = data.loc[wrb_series_indices]
    range_size = float(series_bars[PriceLabel.HIGH].max() - series_bars[PriceLabel.LOW].min())
    wrb_series_indices = sorted(wrb_series_indices)
    return range_size, wrb_series_indices


def _is_bar_wider_than_lookback(
    data: pd.DataFrame,
    current_bar_index: pd.Timestamp,
    lookback_bars: int,
    min_size_increase_pct: float,
    comparison_method: ComparisonMethod = "max"
) -> bool:
    """Check if current bar is wider than lookback bars using specified comparison method.
    
    Args:
        data: Price data
        current_bar_index: Datetime index of the current bar
        lookback_bars: Number of bars to look back
        min_size_increase_pct: Minimum decimal increase required (0.0 to 1.0)
        comparison_method: Method to compare current bar with lookback bars
            - "max": Compare with maximum size in lookback period
            - "avg": Compare with average size of lookback period
            
    Returns:
        bool: True if the current bar is wider than the lookback by the required percentage, False otherwise
        
    Raises:
        IndexError: If current_bar_index or lookback range is out of bounds
        KeyError: If required price columns are missing
        ValueError: If comparison_method is invalid
        ZeroDivisionError: If average lookback size is zero (only for "avg" method)

    TODO:
        1. wrb series :  consecutive bars closing higher or lower are 
        equivalent to a sing WRB
        2. efficient error flow based on guard clauses?
        3. wrb as average or max - what if the function can be functional 
        strategy. i.e pass a function
    """
    try:
        # Get "high-low" ranges for the current and lookback bars
        current_bar_idx = data.index.get_loc(current_bar_index)
        lookback_indices = data.index[current_bar_idx - lookback_bars:current_bar_idx + 1]  # +1 to include current bar

        if len(lookback_indices) <= 1:  # Only current bar or empty
            return False

        lookback_ranges = [
            _get_bar_size(data, idx)
            for idx in lookback_indices
        ]

        cur_bar_range = lookback_ranges[-1]  # Last one is current bar
        lookback_bars_range = lookback_ranges[:-1]  # All except last are lookback bars

        # Calculate reference size based on comparison method
        match comparison_method.lower().strip():
            case "max":
                reference_size = max(lookback_bars_range)
            case "avg":
                reference_size = sum(lookback_bars_range) / len(lookback_bars_range)
                if reference_size == 0:
                    raise ZeroDivisionError("Average lookback bar size is zero")
            case _:
                raise ValueError(f"Invalid comparison method: {comparison_method}. Must be 'max' or 'avg'")
        
        # Calculate size increase as decimal (0.0 to 1.0)
        if reference_size == 0:
            raise ZeroDivisionError("Reference size is zero")
        size_increase = (cur_bar_range - reference_size) / reference_size
        
        return size_increase >= min_size_increase_pct

    except KeyError as e:
        raise KeyError(f"Invalid price data format or missing columns: {e}")
    except IndexError as e:
        raise IndexError(f"Invalid index or lookback range: {e}")
    except ZeroDivisionError:
        raise  # Re-raise as is
    except Exception as e:
        raise RuntimeError(f"Unexpected error in _is_bar_wider_than_lookback: {e}")


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
        is_wider = _is_bar_wider_than_lookback(
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
                'lookback_bars': lookback_bars,
                'min_size_increase_pct': min_size_increase_pct
            }
        )
    except (IndexError, KeyError) as e:
        return create_failure_result(
            data=data,
            step=context.current_step,
            error_msg="Invalid price data format or index",
            e=e
        )
    except ZeroDivisionError as e:
        return create_failure_result(
            data=data,
            step=context.current_step,
            error_msg="Cannot calculate size increase: average bar size is zero",
            e=e
        )
    except Exception as e:
        return create_failure_result(
            data=data,
            step=context.current_step,
            error_msg="Error detecting wide range bar",
            e=e
        ) 