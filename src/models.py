"""Data models for the strategy execution framework."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd


class PriceLabel(StrEnum):
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"


class Direction(StrEnum):
    UP = "UP"
    DOWN = "DOWN"
    RANGE = "RANGE"


@dataclass(frozen=True)
class StrategStepEvaluationResult:
    """
        Used in StrategyExecutionContext to store the result of each step.
        Contains additional data crated by a given step.
    """
    is_success: bool = field(default=False)
    message: str = field(default=None) # FIX : need for this message field?
    timestamp: Optional[pd.Timestamp] = field(default=None) # FIX : determine if this the time of the result or Timestamp in the price data
    step_output: Optional[Dict[str, Any]] = field(default_factory=dict) # side effect data after StrategyStepFn execution


# Method signature for `StrategyStep.evaluation_fn`
StrategyStepFn = Callable[
    [pd.DataFrame, 'StrategyExecutionContext', Dict[str, Any]], 
    StrategStepEvaluationResult
]


@dataclass(frozen=True)
class StrategyStep:
    """A step in a trading strategy execution pipeline.
    Defined in ./config/strategies/[strategy_name].yaml

    `id` and `name` are mandatory
        E.g. 
        name: "Trend Following Strategy"
        steps:
          - id: detect_trend
            name: "Detect Trend"
            description: "Determine if market is trending up, down, or ranging"
            evaluation_fn: "utils.get_trend"
            config: {}
            reevaluates: []
    """
    id: str
    name: str
    description: Optional[str] = None
    
    evaluation_fn: StrategyStepFn = field(hash=False)
    config: Dict[str, Any] = field(hash=False) # parameters for `evaluation_fn`

    # steps that must re-run before this step can 
    # Rationale : ensure prior steps are still valid before evaluating this step
    reevaluates: List['StrategyStep'] = field(default_factory=list, hash=False) 

@dataclass
class StrategyConfig:
    name: str
    steps: List[StrategyStep]

@dataclass
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
             if result.is_success and result.step_output and data_key in result.step_output:
                 if timestamp > latest_timestamp:
                     latest_timestamp = timestamp
                     latest_matching_result = result # Store the result itself

        if latest_matching_result:
             return latest_matching_result.step_output[data_key]

        return None

    def add_result(self, price_data_index : pd.Timestamp, step: StrategyStep, result: StrategStepEvaluationResult) -> None:
        """Adds the result to the context's history IN-PLACE, keyed by (timestamp, step), after validation."""
        
        current_key = (price_data_index, step) # Use the step object itself

        # Data Duplication Validation 
        # Check compares new result.data against ALL existing result.data, 
        # regardless of timestamp, *except* for results from the *exact same step object*.
        # Note: Since step object equality now depends on id, name, description, this 
        # implicitly handles the user's desired check for config mismatches.
        if result.step_output:
            # Iterate over (existing_ts, existing_step_object), existing_result
            for (existing_timestamp, existing_step), existing_result in self.result_history.items(): 
                # Skip results from the exact same step object (or steps considered equal)
                if existing_step == step: 
                    continue 
                # Check if data payload is identical to another *different* step's result data
                if existing_result.step_output and existing_result.step_output == result.step_output:
                     # Now we can use existing_step.name and existing_step.id directly
                     raise ValueError(
                         f"Duplicate result data payload found for key(s) '{list(result.step_output.keys())}'. "
                         f"Step '{step.name}' (ID: {step.id}) at {price_data_index} produced same data as "
                         f"Step '{existing_step.name}' (ID: {existing_step.id}) at {existing_timestamp}."
                     )

        # Modify history in place using (timestamp, step) as key
        self.result_history[current_key] = result 


