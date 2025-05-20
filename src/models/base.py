"""Base classes and interfaces for the strategy execution framework."""

from enum import StrEnum

import pandas as pd


class PriceLabel(StrEnum):
    """Price data column labels.
    
    Values must match the column names in the price data.
    """
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"


class Direction(StrEnum):
    """Market direction indicators."""
    UP = "UP"
    DOWN = "DOWN"
    RANGE = "RANGE"
