"""Data models for the strategy execution framework."""

from dataclasses import dataclass, field
from enum import Enum, StrEnum, auto
from typing import Any, Dict, Optional

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


@dataclass
class StrategStepEvaluationResult:
    success: bool
    message: str
    timestamp: pd.Timestamp = field(default_factory=pd.Timestamp.now)
    data: Optional[Dict[str, Any]] = None

# Add other shared data models here in the future


