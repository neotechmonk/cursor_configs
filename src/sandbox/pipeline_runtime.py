from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd

from src.models import StrategStepEvaluationResult, StrategyExecutionContext

from .models import StrategyStepTemplate


# --- Mapping Helpers ---
def get_value_from_path(obj: dict, path: str) -> Any:
    """
    Get value from nested dictionary using dot notation path.
    Example:
        obj = {"a": {"b": {"c": 42}}}
        path = "a.b.c"
        get_value_from_path(obj, path)  # returns 42
    Args:
        obj: Dictionary to get value from
        path: Dot notation path (e.g. "a.b.c")
    Returns:
        Value at path
    Raises:
        KeyError: If path is invalid
    """
    if not path:
        raise KeyError("Path cannot be empty")
    current = obj
    for key in path.split('.'):
        if key not in current:
            raise KeyError(f"Path '{path}' not found in object")
        current = current[key]
    return current


def prep_arguments_for_strategy_step_function(config: StrategyStepTemplate, context, kwargs) -> dict:
    """
    Map context and config values to function arguments.
    Example:
        config = StrategyStepTemplate(
            pure_function="mock",
            context_inputs={"trend": "context.trend"},
            context_outputs={},
            config_mapping={"frame_size": "config.extreme.frame_size"}
        )
        context = {"trend": "UP"}
        kwargs = {"config": {"extreme": {"frame_size": 5}}}
        prep_arguments_for_strategy_step_function(config, context, kwargs)  # returns {"trend": "UP", "frame_size": 5}
    Args:
        config: StrategyStepTemplate instance
        context: Context object or dict
        kwargs: Additional keyword arguments (e.g., config)
    Returns:
        Dictionary of arguments to pass to the pure function
    """
    args = {}
    for param, path in config.context_inputs.items():
        args[param] = get_value_from_path(context, path)
    for param, path in config.config_mapping.items():
        args[param] = get_value_from_path(kwargs, path)
    return args


def map_strategy_step_function_results(config: StrategyStepTemplate, result: Any) -> dict:
    """
    Map function result to context keys using config context_outputs mapping.
    Handles both dict and non-dict results by wrapping non-dict results in {"result": value}.
    
    Example:
        # With dict result
        config = StrategyStepTemplate(
            pure_function="mock",
            context_inputs={},
            context_outputs={"trend": "analysis.direction"},
            config_mapping={}
        )
        result = {"analysis": {"direction": "UP"}}
        map_strategy_step_function_results(config, result)  # returns {"trend": "UP"}
        
        # With non-dict result
        config = StrategyStepTemplate(
            pure_function="mock",
            context_inputs={},
            context_outputs={"trend": "result"},
            config_mapping={}
        )
        result = Direction.UP
        map_strategy_step_function_results(config, result)  # returns {"trend": Direction.UP}
        
    Args:
        config: StrategyStepTemplate instance
        result: Result from pure function (can be dict or any other type)
    Returns:
        Dictionary mapping context keys to extracted values
    """
    # If result is not a dict, wrap it in {"result": value}
    if not isinstance(result, dict):
        result = {"result": result}
        
    mapped = {}
    for key, path in config.context_outputs.items():
        mapped[key] = get_value_from_path(result, path)
    return mapped


def update_context(context: StrategyExecutionContext, mapped: dict, timestamp=None):
    """
    Update the context with mapped outputs.
    Example:
        mapped = {"trend": "UP", "strength": "strong"}
        update_context(context, mapped, timestamp)
        # context now has these values stored for later steps
    Args:
        context: StrategyExecutionContext instance
        mapped: Dictionary of context keys to values
        timestamp: Optional timestamp for the result
    """
    for context_key, value in mapped.items():
        result_obj = StrategStepEvaluationResult(
            is_success=True,
            message="Step output update",
            step_output={context_key: value},
            timestamp=timestamp
        )
        context.add_result(timestamp, context_key, result_obj)


# --- StepEvaluator ---
@dataclass
class StepEvaluator:
    config: StrategyStepTemplate
    pure_function: Callable

    def __post_init__(self):
        """Validate function signature after initialization."""
        import inspect
        sig = inspect.signature(self.pure_function)
        required_params = set(sig.parameters.keys()) - {'price_feed'}

        for context_key in self.config.context_inputs.keys():
            if context_key not in required_params:
                raise ValueError(f"Pure function missing required parameter from context: {context_key}")

        for config_key in self.config.config_mapping.keys():
            if config_key not in required_params:
                raise ValueError(f"Pure function missing required parameter from config: {config_key}")

    def evaluate(self, price_feed: pd.DataFrame, execution_context: StrategyExecutionContext, **config_params) -> StrategStepEvaluationResult:
        try:
            args = prep_arguments_for_strategy_step_function(self.config, execution_context, config_params)
            result = self.pure_function(price_feed, **args)
            if not isinstance(result, dict):
                result = {"result": result}
            mapped = map_strategy_step_function_results(self.config, result)
            timestamp = price_feed.index[-1] if not price_feed.empty else None
            update_context(execution_context, mapped, timestamp)
            return StrategStepEvaluationResult(
                is_success=True,
                message="Step completed successfully",
                step_output=mapped,
                timestamp=timestamp
            )
        except Exception as e:
            timestamp = price_feed.index[-1] if not price_feed.empty else None
            return StrategStepEvaluationResult(
                is_success=False,
                message=str(e),
                timestamp=timestamp,
                step_output={}
            ) 