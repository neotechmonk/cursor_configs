"""Data models for the strategy execution framework."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

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
    Contains additional data created by a given step.

    Attributes:
        is_success: Whether the step execution was successful
        message: Optional message describing the result
        timestamp: The timestamp from the price data when this result was generated
        step_output: Dictionary of data produced by the step execution
    """
    is_success: bool = field(default=False)
    message: Optional[str] = field(default=None)
    timestamp: Optional[pd.Timestamp] = field(default=None)
    step_output: Optional[Dict[str, Any]] = field(default_factory=dict)


# Type variable for the context parameter to allow for future context types
ContextT = TypeVar('ContextT', bound='StrategyExecutionContext')

# Method signature for `StrategyStep.evaluation_fn`
StrategyStepFn = Callable[
    [pd.DataFrame, ContextT, Dict[str, Any]], 
    StrategStepEvaluationResult
]


@dataclass(frozen=True)
class StrategyStep:
    """A step in a trading strategy execution pipeline.
    Defined in ./config/strategies/[strategy_name].yaml

    Attributes:
        id: Unique identifier for the step; mandatory
        name: Human-readable name of the step; mandatory
        evaluation_fn: Function that evaluates this step; mandatory
        description: Optional description of what the step does
        config: Configuration parameters for the evaluation function
        reevaluates: List of steps that must be re-evaluated before this step

    Example:
        ```yaml
        name: "Trend Following Strategy"
        steps:
          - id: detect_trend
            name: "Detect Trend"
            description: "Determine if market is trending up, down, or ranging"
            evaluation_fn: "utils.get_trend"
            config: {}
            reevaluates: []
        ```
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
    """Configuration for a trading strategy.
    Defined in ./config/strategies/[strategy_name].yaml

    Contains a list of StrategySteps to execute.

    Example:
        ```yaml
        name: "Trend Following Strategy"
        steps:
          - id: detect_trend
            name: "Detect Trend"

    Attributes:
        name: Name of the strategy
        steps: Ordered list of steps to execute
    """
    name: str
    steps: List[StrategyStep]


@dataclass
class StrategyExecutionContext:
    """Mutable context holding results history for a strategy run.
    Uses (price_data_index, step) tuple as key and result as value.
    
    This context is:
    - created when a strategy is applied to price data 
    - destroyed when the strategy is reset or trade is determined
    - Evaluation of each `StrategyStep.evaluation_fn()` will add a new `StrategStepEvaluationResult`
    - A given strategy could have multiple `StrategStepEvaluationResult`s due to revaluations

    Attributes:
    _strategy_steps_results: Main storage mapping (timestamp, step) to results
    _latest_results_cache: Cache for quick access to latest successful results
    """
    _strategy_steps_results: Dict[Tuple[pd.Timestamp, StrategyStep], StrategStepEvaluationResult] = field(default_factory=dict) # succcessful and failed results
    _latest_results_cache: Dict[str, Any] = field(default_factory=dict) # latest successful outputs from StrategySteps

    def _validate_no_duplicate_outputs_by_different_steps(
        self,
        cur_step: StrategyStep,
        cur_step_result: StrategStepEvaluationResult,
        prev_results: Dict[Tuple[pd.Timestamp, StrategyStep], StrategStepEvaluationResult]
    ) -> None:
        """Ensure only one step produces a given output.

        Args:
            cur_step: The current step being validated
            cur_step_result: The result from the current step
            prev_results: Previous results to check against

        Raises:
            ValueError: If another step has already produced the same output - eliminates risk of the output from a step being overwritten by another step
        """
        if not cur_step_result.step_output:
            return
            
        for (_, existing_step), existing_result in prev_results.items():
            if (existing_step != cur_step 
                and existing_result.step_output 
                and existing_result.step_output == cur_step_result.step_output):
                raise ValueError(
                    f"Steps '{cur_step.name}' and '{existing_step.name}' "
                    f"produced identical output: {list(cur_step_result.step_output.keys())}. "
                    "Two StrategySteps cannot produce the same output."
                )
    def _validate_identical_output_by_different_steps(
        self,
        cur_step: StrategyStep,
        cur_step_result: StrategStepEvaluationResult,
        prev_results: Dict[Tuple[pd.Timestamp, StrategyStep], StrategStepEvaluationResult]
        ) -> None:
        """
            Ensure that different StrategySteps do not produce identical outputs.

            If two different steps produce the same output, it indicates a bug - error out.
        """
        if not cur_step_result.step_output:
            return
            
        for (_, existing_step), existing_result in prev_results.items():
            if (existing_step != cur_step 
                and existing_result.step_output 
                and existing_result.step_output == cur_step_result.step_output):
                raise ValueError(
                    f"Steps '{cur_step.name}' and '{existing_step.name}' "
                    f"produced identical output: {list(cur_step_result.step_output.keys())}. "
                    "Two different StrategySteps cannot produce the same output."
                )

    def _validate_step_output_keys_and_values(
        self,
        step: StrategyStep,
        result: StrategStepEvaluationResult
    ) -> None:
        """Validate that step output keys and values are non-empty.
        
        Args:
            step: The strategy step being validated
            result: The result containing the output to validate
            
        Raises:
            ValueError: If any key or value in the output is empty
        """
        if not result.step_output:
            return
            
        for key, value in result.step_output.items():
            if not key or not key.strip():
                raise ValueError(f"Step '{step.name}' produced output with empty key")
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Step '{step.name}' produced output with empty value for key '{key}'")
            
    def get_latest_strategey_step_output_result(self, lookup_key: str) -> Optional[Any]:
        """Find the latest successful data value for a given key in the cache.
        
        Args:
            lookup_key: The key to look up in the cache
            
        Returns:
            The latest value for the key, or None if not found
        """
        if lookup_key in self._latest_results_cache:
            return self._latest_results_cache[lookup_key]
        
        return None
    
    def get_all_strategey_step_output_results(self, lookup_key: str) -> Optional[Any]:
        """Find all results for a given key in the results history.
        
        Args:
            lookup_key: The key to look up in the results history
            
        Returns:
            All values for the key, or None if not found
        """
        if lookup_key in self._strategy_steps_results:
            return self._strategy_steps_results[lookup_key]
        
        return None

    def add_result(self, price_data_index: pd.Timestamp, step: StrategyStep, result: StrategStepEvaluationResult) -> None:
        """Add new result to context with validation.
        
        Args:
            price_data_index: The timestamp from the price data
            step: The step that produced the result
            result: The result to add
            
        Raises:
            ValueError: If validation fails (duplicate outputs, empty keys/values)
        """
        current_key = (price_data_index, step)

        # Validations
        self._validate_step_output_keys_and_values(step, result) 
        self._validate_no_duplicate_outputs_by_different_steps(
            cur_step=step, 
            cur_step_result=result, 
            prev_results=self._strategy_steps_results
        )
        self._validate_identical_output_by_different_steps(
            cur_step=step, 
            cur_step_result=result, 
            prev_results=self._strategy_steps_results
        )

        # Add to results history and the add/update cache
        self._strategy_steps_results[current_key] = result
        
        # only successful results are with outputs are cached
        if result.is_success and result.step_output:
            self._latest_results_cache.update(result.step_output)

    # # TODO : YAGNI
    # def get_data_producers(self, data_key: str) -> Set[str]:
    #     """Get IDs of steps that have produced this data key."""
    #     return {step.id for (_, step), result in self._strategy_steps_results.items() 
    #             if result.step_output and data_key in result.step_output}

    # # TODO : YAGNI
    # def get_data_timeline(self, data_key: str) -> List[pd.Timestamp]:
    #     """Get ordered price data timestamp of when data key was produced/modified.
    #     Note: this is not the system time of StrategyStep execution.
    #     """
    #     return sorted(timestamp for (timestamp, _), result in self._strategy_steps_results.items() 
    #                  if result.step_output and data_key in result.step_output)


