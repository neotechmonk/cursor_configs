from enum import Enum, StrEnum, auto

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


def detect_direction(price_feed: pd.DataFrame) -> Direction:
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


def main():
    raise NotImplementedError()

if __name__ == "main":
    pass
    # main()