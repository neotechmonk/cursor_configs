"""Data models for the strategy execution framework."""

import bisect
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import pandas as pd


class PriceLabel(StrEnum):
    # Values must match the column names in the price data
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
    evaluation_fn: StrategyStepFn = field(hash=False)
    description: Optional[str] = field(default=None)
    config: Dict[str, Any] = field(hash=False, default_factory=dict) # parameters for `evaluation_fn`
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
    Uses (price_data_index, step) tuple as key and result as value.
    
    Usage : 
    - created when a strategy is applied to a price data 
    - destroyed when the strategy is reset or trade is determined
    - Evaluation of each `StrategyStep.evaluation_fn()` will add a new `StrategStepEvaluationResult`
    - A given strategy could have multiple `StrategStepEvaluationResult`s due to revaluations
    """
    # Main storage - single source of truth
    strategy_steps_results: Dict[Tuple[pd.Timestamp, StrategyStep], StrategStepEvaluationResult] = field(default_factory=dict)
    # Cache for performance
    _latest_results_cache: Dict[str, Any] = field(default_factory=dict)

    def _validate_no_duplicate_outputs_by_different_steps(
        self,
        cur_step: StrategyStep,
        cur_step_result: StrategStepEvaluationResult,
        prev_results: Dict[Tuple[pd.Timestamp, StrategyStep], StrategStepEvaluationResult]
        ) -> None:
        """
            Ensure only the a give StrategyStep produces the step output. 

            More than one step producing the same output is an indication of a bug - error out.
        """
        if not cur_step_result.step_output:
            return
            
        for (_, existing_step), existing_result in prev_results.items():
            if (existing_step != cur_step 
                and existing_result.step_output 
                and existing_result.step_output == cur_step_result.step_output):
                raise ValueError(
                    f"Steps '{cur_step.name}' and '{existing_step.name}' \
                        produced identical output: {list(cur_step_result.step_output.keys())}.\
                            Two StrategySteps cannot produce the same output."
                        )
            
    def get_latest_strategey_step_output_result(self, lookup_key: str) -> Optional[Any]:
        """Find the latest successful data value for a given key in the cache.
            `add_result()` adds to the cache.
        """
        if lookup_key in self._latest_results_cache:
            return self._latest_results_cache[lookup_key]
        
        return None
    
    def get_all_strategey_step_output_results(self, lookup_key: str) -> Optional[Any]:
        """Find the latest successful data value for a given key in the cache.
            `add_result()` adds to the cache.
        """
        if lookup_key in self.strategy_steps_results:
            return self.strategy_steps_results[lookup_key]
        
        return None

    def add_result(self, price_data_index: pd.Timestamp, step: StrategyStep, result: StrategStepEvaluationResult) -> None:
        """Add new result to context with validation."""
        current_key = (price_data_index, step)

        #Validations
        self._validate_no_duplicate_outputs_by_different_steps(step, result, self.strategy_steps_results)

        # Add to results history and the add/update cache
        self.strategy_steps_results[current_key] = result
        
        # only successful results are with outputs are cached
        if result.is_success and result.step_output:
            self._latest_results_cache.update(result.step_output)

    # TODO : YAGNI
    def get_data_producers(self, data_key: str) -> Set[str]:
        """Get IDs of steps that have produced this data key."""
        return {step.id for (_, step), result in self.strategy_steps_results.items() 
                if result.step_output and data_key in result.step_output}

    # TODO : YAGNI
    def get_data_timeline(self, data_key: str) -> List[pd.Timestamp]:
        """Get ordered price data timestamp of when data key was produced/modified.
        Note: this is not the system time of StrategyStep execution.
        """
        return sorted(timestamp for (timestamp, _), result in self.strategy_steps_results.items() 
                     if result.step_output and data_key in result.step_output)


