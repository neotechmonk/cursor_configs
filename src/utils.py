from typing import Optional

import pandas as pd

from models import Direction, PriceLabel


def get_trend(price_feed: pd.DataFrame) -> Direction:
    """
        UP : lowest point in the frame was before the highest point
        DOWN : highest point in the frame was before the lowest point 
        RANGE : current price is within pct of collection of pivot highs and lows
    """
    if (hi_idx := price_feed[PriceLabel.HIGH].idxmax()) > (lo_idx := price_feed[PriceLabel.HIGH].idxmin()):
        return Direction.UP
    elif hi_idx < lo_idx:
        return Direction.DOWN
    else:
        return Direction.RANGE


def is_extreme_bar(price_feed: pd.DataFrame, trend: Direction, frame_size:Optional[int] = None)-> bool:

        # guards
        if trend not in (Direction.UP, Direction.DOWN):
            raise ValueError("Market must trend UP or DOWN")
       
        price_feed_len = len(price_feed)

        if  frame_size is None: 
            frame_size = price_feed_len
        
        if frame_size < 1:
            raise ValueError("Frame size must be at least 1")
        
        if frame_size > price_feed_len:
            raise ValueError("Frame size is larger the bars in the `price_feed`")
        
        # Get current bar (most recent)
        recent_bar = price_feed.iloc[-1]

        # Get previous bars for the comparison window
        history = price_feed.iloc[-frame_size:-1]

        match trend:
            case Direction.UP:
                return recent_bar[PriceLabel.HIGH] > history[PriceLabel.HIGH].max()
            case Direction.DOWN:
                return recent_bar[PriceLabel.LOW] < history[PriceLabel.LOW].min()
            case _:
                return False


# TODO : Refactor this to be a generic function that confirms number of bars since reference index
def is_bars_since_extreme_pivot_valid(price_feed: pd.DataFrame, major_swing_high_idx, min_bars: int, max_bars: int) -> bool:
    price_feed_len = len(price_feed)

    if max_bars is None:
        max_bars = price_feed_len

    major_idx_pos = price_feed.index.get_loc(major_swing_high_idx)
    bars_since_swing_high = price_feed_len - major_idx_pos - 1  # Exclude swing high bar itself

    return min_bars <= bars_since_swing_high <= max_bars


# FIX : Refactor to match generalistation 
def is_within_fib_extension(
    price_feed: pd.DataFrame,
    trend: Direction,
    ref_swing_start_idx: pd.Timestamp,
    ref_swing_end_idx: pd.Timestamp,
    min_fib_extension: float = 1.35,
    max_fib_extension: float = 1.875
) -> bool:
    
    # --- Guards ---
    if trend not in (Direction.UP, Direction.DOWN):
        raise ValueError(f"Unsupported trend: {trend}. Must be Direction.UP or Direction.DOWN.")
    
    if not isinstance(min_fib_extension, (int, float)) or not isinstance(max_fib_extension, (int, float)):
        raise TypeError("min_fib_extension and max_fib_extension must be numeric (int or float).")
    
    if ref_swing_start_idx >= ref_swing_end_idx:
        raise ValueError(
            f"Invalid pullback indices: start={ref_swing_start_idx} must be before end={ref_swing_end_idx}."
        )

    match trend:
        case Direction.UP:
            current_high = price_feed.iloc[-1][PriceLabel.HIGH]
            pullback_high = price_feed.at[ref_swing_start_idx, PriceLabel.HIGH]
            pullback_low = price_feed.at[ref_swing_end_idx, PriceLabel.LOW]

            pullback_distance = pullback_high - pullback_low
            if pullback_distance == 0:
                raise ValueError("Previous pullback swing is invalid (zero distance).")

            impulse_length = current_high - pullback_low
            fib_extension = impulse_length / pullback_distance

        case Direction.DOWN:
            current_low = price_feed.iloc[-1][PriceLabel.LOW]
            pullback_low = price_feed.at[ref_swing_start_idx, PriceLabel.LOW]
            pullback_high = price_feed.at[ref_swing_end_idx, PriceLabel.HIGH]

            pullback_distance = pullback_high - pullback_low
            if pullback_distance == 0:
                raise ValueError("Previous pullback swing is invalid (zero distance).")

            impulse_length = pullback_high - current_low
            fib_extension = impulse_length / pullback_distance

            # print(f"{current_low=}, {pullback_low=}, {pullback_high=}, {pullback_distance=}, {fib_extension=}")

        case _:
            raise ValueError("Trend must be either Direction.UP or Direction.DOWN.")

    return min_fib_extension <= fib_extension <= max_fib_extension


def is_last_bar_within_bars_count(
    price_feed: pd.DataFrame,
    ref_bar_idx: pd.Timestamp,
    searched_bar_idx: Optional[pd.Timestamp] = None,
    min_bars: int = None,
    max_bars: int = None,
) -> bool:
    # --- Guards ---
    if not isinstance(min_bars, int) or not isinstance(max_bars, int):
        raise TypeError("min_bars and max_bars must be integers.")

    # Default to last bar if searched_bar_idx is not provided
    if searched_bar_idx is None:
        searched_bar_idx = price_feed.index[-1]

    if searched_bar_idx < ref_bar_idx:
        raise ValueError(f"Reference index {ref_bar_idx} should precede searched index {searched_bar_idx}.")
    
    try:
        ref_idx_pos = price_feed.index.get_loc(ref_bar_idx)
    except KeyError:
        raise ValueError(f"Reference index {ref_bar_idx} not in price feed.")

    try:
        ser_idx_pos = price_feed.index.get_loc(searched_bar_idx)
    except KeyError:
        raise ValueError(f"Searched index {searched_bar_idx} not in price feed.")

    bars_since_ref = ser_idx_pos - ref_idx_pos

    return min_bars <= bars_since_ref <= max_bars
