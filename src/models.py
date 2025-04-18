"""Data models for the strategy execution framework."""

from dataclasses import dataclass, field
from enum import Enum, StrEnum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

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


# Forward reference for StrategyExecutionContext needed in StrategyStepFn
StrategyStepFn = Callable[
    [pd.DataFrame, 'StrategyExecutionContext', Dict[str, Any]], 
    StrategStepEvaluationResult
]


@dataclass
class StrategyStep:
    id: str  # Unique identifier
    name: str
    description: str
    evaluation_fn: StrategyStepFn 
    config: Dict[str, Any]
    reevaluates: List['StrategyStep'] = field(default_factory=list)


@dataclass()
class StrategyExecutionContext:
    """Mutable context holding results history for a strategy run."""
    # Stores the (step, result) tuple keyed by timestamp encountered so far in this run
    result_history: Dict[pd.Timestamp, Tuple[StrategyStep, StrategStepEvaluationResult]] = field(default_factory=dict)

    def find_latest_successful_data(self, data_key: str) -> Optional[Any]:
        """Finds the data value from the latest successful result containing the data_key.
        
        Searches the results of all steps encountered so far (keyed by timestamp)
        in reverse chronological order.
        Returns the data value associated with data_key or None.
        """
        latest_matching_result = None
        latest_timestamp = pd.Timestamp.min

        for timestamp, (step, result) in self.result_history.items():
             if result.success and result.data and data_key in result.data:
                 if timestamp > latest_timestamp:
                     latest_timestamp = timestamp
                     latest_matching_result = result

        if latest_matching_result:
             return latest_matching_result.data[data_key]

        return None

    def add_result(self, price_data_index : pd.Timestamp, step: StrategyStep, result: StrategStepEvaluationResult) -> None:
        """Adds the result to the context's history IN-PLACE, keyed by timestamp, after validation."""
        # Data Duplication Validation 
        if result.data:
            for existing_timestamp, (existing_step, existing_result) in self.result_history.items():
                if existing_step.id == step.id: 
                    continue
                if existing_result.data and existing_result.data == result.data:
                    raise ValueError(
                        f"Duplicate result data payload found for key(s) '{list(result.data.keys())}'. "
                        f"Step '{step.name}' (ID: {step.id}) at {price_data_index} produced same data as "
                        f"Step '{existing_step.name}' (ID: {existing_step.id}) at {existing_timestamp}."
                    )

        # Modify history in place
        self.result_history[price_data_index] = (step, result) 
        # No return needed (or return self if preferred, but None is typical for in-place modification)


# Add other shared data models here in the future


@dataclass
class StrategyConfig:
    name: str
    steps: List[StrategyStep]