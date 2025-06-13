"""Strategy-specific models for the strategy execution framework."""

from importlib import import_module
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models.system import StrategyStepTemplate
from src.validation.validators import (
    validate_identical_output_by_different_steps,
    validate_no_duplicate_outputs_by_different_steps,
    validate_step_output_keys_and_values,
)

# Method signature for strategy step evaluation functions
StrategyStepEvalFn = Callable[
    [pd.DataFrame, 'StrategyExecutionContext', Dict[str, Any]], 
    'StrategyStepEvaluationResult'
]


class StrategyStepEvaluationResult(BaseModel):
    """Result of a strategy step evaluation.
    
    Used in StrategyExecutionContext to store the result of each step.
    Contains additional data created by a given step.

    Attributes:
        is_success: Whether the step execution was successful
        message: Optional message describing the result
        timestamp: The timestamp from the price data when this result was generated
        step_output: Dictionary of data produced by the step execution
    """
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    is_success: bool = Field(default=False)
    message: Optional[str] = Field(default=None)
    timestamp: Optional[pd.Timestamp] = Field(default=None)
    step_output: Optional[Dict[str, Any]] = Field(default_factory=dict)


class StrategyStep(BaseModel):
    """A step in a trading strategy execution pipeline.
    
    Defined in ./config/strategies/[strategy_name].yaml

    Attributes:
        system_step_id: ID of the system step template to use (e.g. "detect_trend")
        description: Optional description of what the step does
        static_config: Static configuration parameters for the step
        dynamic_config: Mapping of dynamic input parameters to their sources
        reevaluates: List of steps that must be re-evaluated before this step
        template: Reference to the StrategyStepTemplate this step uses
        evaluation_fn: The function that evaluates this step (loaded from template.function)

    Example:
        ```yaml
        name: "Trend Following Strategy"
        steps:
          - system_step_id: detect_trend
            description: "Determine the current market trend direction"
            static_config: {}
            dynamic_config: {}
        ```
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    system_step_id: str
    description: Optional[str] = Field(default=None)
    static_config: Dict[str, Any] = Field(default_factory=dict)
    dynamic_config: Dict[str, str] = Field(default_factory=dict)
    reevaluates: List['StrategyStep'] = Field(default_factory=list)
    template: StrategyStepTemplate  # Required field, no default
    _evaluation_fn: Optional[StrategyStepEvalFn] = None  # Private field for caching

    @property
    def evaluation_fn(self) -> StrategyStepEvalFn:
        """Get the evaluation function for this step.
        
        The function is loaded from the template's function path if not already loaded.
        
        Returns:
            The evaluation function for this step
            
        Raises:
            ImportError: If the function cannot be imported
            AttributeError: If the function is not found in the module
        """
        if self._evaluation_fn is None:
            module_path, fn_name = self.template.function.rsplit(".", 1)
            try:
                module = import_module(module_path)
                self._evaluation_fn = getattr(module, fn_name)
            except ImportError as e:
                raise ImportError(f"Could not import module {module_path} for step {self.system_step_id}: {e}")
            except AttributeError as e:
                raise AttributeError(f"Function {fn_name} not found in module {module_path} for step {self.system_step_id}: {e}")
        return self._evaluation_fn

    @evaluation_fn.setter
    def evaluation_fn(self, fn: StrategyStepEvalFn) -> None:
        """Set the evaluation function for this step.
        
        This is primarily used for testing.
        
        Args:
            fn: The evaluation function to use
        """
        self._evaluation_fn = fn

    @model_validator(mode='after')
    def validate_config_against_template(self) -> 'StrategyStep':
        """Validate that the configuration matches the template requirements.
        
        Returns:
            The validated model instance
            
        Raises:
            ValueError: If configuration is invalid
        """
        errors = []
        
        # Validate static config matches template's config_mapping
        for param_name in self.static_config:
            if param_name not in self.template.config_mapping:
                errors.append(
                    f"Static config parameter '{param_name}' not found in template config_mapping"
                )
                
        # Validate dynamic config matches template's input_params_map
        for param_name in self.dynamic_config:
            if param_name not in self.template.input_params_map:
                errors.append(
                    f"Dynamic config parameter '{param_name}' not found in template input_params_map"
                )
        
        if errors:
            raise ValueError("\n".join(errors))
                    
        return self

    def __hash__(self) -> int:
        return hash((self.system_step_id, self.description))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StrategyStep):
            return NotImplemented
        return (self.system_step_id, self.description) == (
            other.system_step_id, other.description
        )


class StrategyConfig(BaseModel):
    """Configuration for a trading strategy.
    
    Defined in ./config/strategies/[strategy_name].yaml

    Contains a list of StrategySteps to execute.

    Example:
        ```yaml
        name: "Trend Following Strategy"
        steps:
          - id: detect_trend
            name: "Detect Trend"
        ```

    Attributes:
        name: Name of the strategy
        steps: Ordered list of steps to execute
    """
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    name: str
    steps: List[StrategyStep]


class StrategyExecutionContext(BaseModel):
    """Mutable context holding results history for a strategy run.
    
    Uses (price_data_index, step) tuple as key and result as value.
    
    This context is:
    - created when a strategy is applied to price data 
    - destroyed when the strategy is reset or trade is determined
    - Evaluation of each `StrategyStep.evaluation_fn()` will add a new `StrategyStepEvaluationResult`
    - A given strategy could have multiple `StrategyStepEvaluationResult`s due to revaluations

    Attributes:
        strategy_steps_results: Main storage mapping (timestamp, step) to results
        latest_results_cache: Cache for quick access to latest successful results
    """
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    strategy_steps_results: Dict[Tuple[pd.Timestamp, StrategyStep], StrategyStepEvaluationResult] = Field(
        default_factory=dict
    )
    latest_results_cache: Dict[str, Any] = Field(
        default_factory=dict
    )

    def get_latest_strategey_step_output_result(self, lookup_key: str) -> Optional[Any]:
        """Find the latest successful data value for a given key in the cache.
        
        Args:
            lookup_key: The key to look up in the cache
            
        Returns:
            The latest value for the key, or None if not found
        """
        if lookup_key in self.latest_results_cache:
            return self.latest_results_cache[lookup_key]
        
        return None
    
    def get_all_strategey_step_output_results(self, lookup_key: str) -> Optional[Any]:
        """Find all results for a given key in the results history.
        
        Args:
            lookup_key: The key to look up in the results history
            
        Returns:
            All values for the key, or None if not found
        """
        if lookup_key in self.strategy_steps_results:
            return self.strategy_steps_results[lookup_key]
        
        return None

    def add_result(self, price_data_index: pd.Timestamp, step: StrategyStep, result: StrategyStepEvaluationResult) -> None:
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
        validate_step_output_keys_and_values(step, result) 
        validate_no_duplicate_outputs_by_different_steps(
            cur_step=step, 
            cur_step_result=result, 
            prev_results=self.strategy_steps_results
        )
        validate_identical_output_by_different_steps(
            cur_step=step,
            cur_step_result=result,
            prev_results=self.strategy_steps_results
        )

        # Add to results history and the add/update cache
        self.strategy_steps_results[current_key] = result
        
        # only successful results are with outputs are cached
        if result.is_success and result.step_output:
            self.latest_results_cache.update(result.step_output)
