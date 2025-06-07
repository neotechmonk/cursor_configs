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
    lookback_bars: int,
    lookback_start_idx: pd.Timestamp | None = None
) -> bool:
    """Validate if there are enough bars for the lookback period.
    
    Args:
        data: Price data to analyze
        lookback_bars: Number of bars to look back
        lookback_start_idx: Optional start index for lookback period. If None,
            the latest bar index will be used. This is useful when validating
            lookback for a WRB series.
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValueError: If data is empty or insufficient bars for lookback period
        IndexError: If lookback_start_idx is not in data index
    """
    # Guard clause for empty data
    if data.empty:
        raise ValueError("No data available")
    
    if len(data) < lookback_bars:
        raise ValueError(f"Not enough bars for lookback period. Required: {lookback_bars}, Available: {len(data)}")
    
    # If no start index provided, use the latest bar index
    if lookback_start_idx is None:
        lookback_start_idx = data.index[-1]
    
    # Validate start index exists
    if lookback_start_idx not in data.index:
        raise IndexError(f"Lookback start index {lookback_start_idx} not found in data")
    
    # Check if there are enough bars before start index
    start_pos = data.index.get_loc(lookback_start_idx)
    if start_pos < lookback_bars:
        return False
    
    return True


def _get_high_low_range_abs(
    price_data: pd.DataFrame,
    current_bar_index: pd.Timestamp,
) -> float:
    """Calculate the high-low range of a single bar.
    
    Args:
        price_data: Price data
        current_bar_index: Datetime index of the current bar
        
    Returns:
        float: high-low range of the bar
        
    Raises:
        IndexError: If current_bar_index is not in the DataFrame index
        KeyError: If required price columns are missing
    """
    if current_bar_index not in price_data.index:
        raise IndexError(f"Current bar index {current_bar_index} not found in data")

    bar = price_data.loc[current_bar_index]
    return float(bar[PriceLabel.HIGH] - bar[PriceLabel.LOW])


def _get_wide_range_bar(
    price_data: pd.DataFrame,
    current_bar_index: pd.Timestamp,
) -> tuple[float, list[pd.Timestamp]]:
    """Calculate the range of a wide range bar series in a trend.
    
    A wide range bar series is defined as consecutive bars where either:
    For uptrend:
    1. Each bar's high is higher than the previous bar's high
    2. Each bar's low is higher than the previous bar's low
    3. Each bar's close is higher than the previous bar's high
    
    OR for downtrend:
    1. Each bar's low is lower than the previous bar's low
    2. Each bar's high is lower than the previous bar's high
    3. Each bar's close is lower than the previous bar's low
    
    Args:
        price_data: Price data
        current_bar_index: Datetime index of the current bar
        
    Returns:
        tuple[float, list[pd.Timestamp]]: (high-low range of the series, list of indices in the series)
        
    Raises:
        IndexError: If current_bar_index is not in the DataFrame index
        KeyError: If required price columns are missing
    """
    if current_bar_index not in price_data.index:
        raise IndexError(f"Current bar index {current_bar_index} not found in data")

    current_pos = price_data.index.get_loc(current_bar_index)
    # If current bar is the very first bar, cannot be a WRB
    if current_pos == 0:
        return float('nan'), []

    wrb_series_indices = []
    for pos in range(current_pos, 0, -1):
        curr_bar = price_data.iloc[pos]
        prev_bar = price_data.iloc[pos-1]
        curr_idx = price_data.index[pos]

        # First determine if we're in an uptrend or downtrend
        is_uptrend = all([curr_bar[PriceLabel.HIGH] > prev_bar[PriceLabel.HIGH],\
                          curr_bar[PriceLabel.LOW] > prev_bar[PriceLabel.LOW],\
                          curr_bar[PriceLabel.CLOSE] > prev_bar[PriceLabel.HIGH]])
        
        is_downtrend = all([curr_bar[PriceLabel.LOW] < prev_bar[PriceLabel.LOW],\
                            curr_bar[PriceLabel.HIGH] < prev_bar[PriceLabel.HIGH],\
                          curr_bar[PriceLabel.CLOSE] < prev_bar[PriceLabel.LOW]])
        
        # both uptrend and downtrend cannot happen at the same time : unrealistic in real market
        if is_uptrend and is_downtrend:
            break
        
        # No trend, not a WRB E.g. both HH/LL, cur and prev bar have same H and L
        if not is_uptrend and not is_downtrend:
            break

        # Clear up or down trend (not both or neither)
        wrb_series_indices.append(curr_idx)
    
    if not wrb_series_indices:
        return float('nan'), []

    wrb_series = price_data.loc[wrb_series_indices]
    wrb_range = float(wrb_series[PriceLabel.HIGH].max() - wrb_series[PriceLabel.LOW].min())
    return wrb_range, sorted(wrb_series_indices)


def _is_bar_wider_than_lookback(
    data: pd.DataFrame,
    current_bar_index: pd.Timestamp,
    lookback_bars: int,
    min_size_increase_pct: float,
    comparison_method: ComparisonMethod = "max"
) -> bool:
    """Check if current bar is wider than lookback bars using specified comparison method."""
    print(f"\nDEBUG: Starting _is_bar_wider_than_lookback")
    print(f"DEBUG: current_bar_index={current_bar_index}, lookback_bars={lookback_bars}, min_size_increase_pct={min_size_increase_pct}, comparison_method={comparison_method}")

    # 1. get the single bar WRB or consequtive bar WRB
    wrb_range, wrb_indices = _get_wide_range_bar(price_data=data, current_bar_index=current_bar_index)
    print(f"DEBUG: wrb_range={wrb_range}, wrb_indices={wrb_indices}")

    # if current or recent bars did not form a WRB, return False
    if not wrb_range and not wrb_indices:
        print("DEBUG: No WRB detected, returning False")
        return False

    # 2. Check if min lookback bars are available relative to the current bar
    # Get the position of the current bar index
    current_pos = data.index.get_loc(current_bar_index)
    # We need at least lookback_bars before the current bar
    if current_pos < lookback_bars:
        print("DEBUG: Insufficient lookback bars, returning False")
        return False

    # 3. Check if WRB satisfies the min growth percentage
    # Calculate reference size based on comparison method
    comparison_methods = {
        "max": lambda x: max(x),
        "avg": lambda x: sum(x) / len(x)
    }
    
    # guard : unsupported comparison method
    if (method := comparison_method.lower().strip()) not in comparison_methods:
        raise ValueError(f"Invalid comparison method: {comparison_method}. Must be 'max' or 'avg'")
    
    # Get the lookback period indices - look back from the current bar
    lookback_start_idx = current_pos - lookback_bars
    lookback_indices = data.index[lookback_start_idx:current_pos]
    print(f"DEBUG: lookback_indices={lookback_indices}")

    # Calculate ranges for each bar in lookback period
    lookback_ranges = [
        _get_high_low_range_abs(data, idx)
        for idx in lookback_indices
    ]
    print(f"DEBUG: lookback_ranges={lookback_ranges}")

    # Get the comparison function and calculate reference size
    comp_result = comparison_methods[method](lookback_ranges)
    print(f"DEBUG: comp_result={comp_result}")

    # guard : arithmetic error
    if comp_result == 0:
        raise ZeroDivisionError("Reference size is zero")
    
    size_increase = wrb_range/comp_result - 1
    print(f"DEBUG: size_increase={size_increase}, min_size_increase_pct={min_size_increase_pct}")
    print(f"DEBUG: Final result: {size_increase >= min_size_increase_pct}")
    
    return size_increase >= min_size_increase_pct


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
    is_valid = _validate_lookup_bars(data, lookback_bars)
    if not is_valid:
        return create_failure_result(
            data=data,
            step=context.current_step,
            error_msg="Not enough bars for the lookback period"
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