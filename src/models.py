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


@dataclass(frozen=True)
class StrategStepEvaluationResult:
    success: bool
    message: str
    timestamp: Optional[pd.Timestamp] = None
    data: Optional[Dict[str, Any]] = field(default_factory=dict)


# Forward reference for StrategyExecutionContext needed in StrategyStepFn
StrategyStepFn = Callable[
    [pd.DataFrame, 'StrategyExecutionContext', Dict[str, Any]], 
    StrategStepEvaluationResult
]


@dataclass(frozen=True)
class StrategyStep:
    id: str  # Unique identifier
    name: str
    description: str
    # Exclude non-hashable or complex types from hash calculation
    evaluation_fn: StrategyStepFn = field(hash=False)
    config: Dict[str, Any] = field(hash=False)
    reevaluates: List['StrategyStep'] = field(default_factory=list, hash=False)


@dataclass()
class StrategyExecutionContext:
    """Mutable context holding results history for a strategy run.
    Uses (price_data_index, step) tuple as key and result as value."""
    # Key uses the StrategyStep object itself (hashable due to field exclusions)
    result_history: Dict[Tuple[pd.Timestamp, StrategyStep], StrategStepEvaluationResult] = field(default_factory=dict)

    def find_latest_successful_data(self, data_key: str) -> Optional[Any]:
        """Finds the data value from the latest successful result containing the data_key.
        
        Searches the results of all steps encountered so far (keyed by timestamp, step)
        in reverse chronological order based on timestamp.
        Returns the data value associated with data_key or None.
        """
        latest_matching_result = None
        latest_timestamp = pd.Timestamp.min

        # Iterate through (timestamp, step_object), result pairs
        for (timestamp, step_object), result in self.result_history.items():
             if result.success and result.data and data_key in result.data:
                 if timestamp > latest_timestamp:
                     latest_timestamp = timestamp
                     latest_matching_result = result # Store the result itself

        if latest_matching_result:
             return latest_matching_result.data[data_key]

        return None

    def add_result(self, price_data_index : pd.Timestamp, step: StrategyStep, result: StrategStepEvaluationResult) -> None:
        """Adds the result to the context's history IN-PLACE, keyed by (timestamp, step), after validation."""
        
        current_key = (price_data_index, step) # Use the step object itself

        # Data Duplication Validation 
        # Check compares new result.data against ALL existing result.data, 
        # regardless of timestamp, *except* for results from the *exact same step object*.
        # Note: Since step object equality now depends on id, name, description, this 
        # implicitly handles the user's desired check for config mismatches.
        if result.data:
            # Iterate over (existing_ts, existing_step_object), existing_result
            for (existing_timestamp, existing_step), existing_result in self.result_history.items(): 
                # Skip results from the exact same step object (or steps considered equal)
                if existing_step == step: 
                    continue 
                # Check if data payload is identical to another *different* step's result data
                if existing_result.data and existing_result.data == result.data:
                     # Now we can use existing_step.name and existing_step.id directly
                     raise ValueError(
                         f"Duplicate result data payload found for key(s) '{list(result.data.keys())}'. "
                         f"Step '{step.name}' (ID: {step.id}) at {price_data_index} produced same data as "
                         f"Step '{existing_step.name}' (ID: {existing_step.id}) at {existing_timestamp}."
                     )

        # Modify history in place using (timestamp, step) as key
        self.result_history[current_key] = result 


@dataclass
class StrategyConfig:
    name: str
    steps: List[StrategyStep]