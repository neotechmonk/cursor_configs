from enum import Enum, StrEnum, auto
from typing import Optional

import pandas as pd


class PriceLabel(StrEnum):
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    RANGE = auto()


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
                return recent_bar[PriceLabel.HIGH.value] > history[PriceLabel.HIGH.value].max()
            case Direction.DOWN:
                return recent_bar[PriceLabel.LOW.value] < history[PriceLabel.LOW.value].min()
            case _:
                return False
            

def main():
    raise NotImplementedError()

if __name__ == "main":
    pass
    # main()