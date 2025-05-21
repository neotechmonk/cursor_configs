"""Strategy step implementation using pipeline configuration."""

from typing import Any, Callable, Dict

import pandas as pd

from src.models import StrategStepEvaluationResult, StrategyExecutionContext


class StrategyStep:
    """Strategy step that uses pipeline configuration to manage inputs/outputs."""
    
    def __init__(self, step_config: Dict[str, Any], pure_function: Callable):
        """Initialize strategy step.
        
        Args:
            step_config: Configuration for this step
            pure_function: The pure function to execute
        """
        self.step_config = step_config
        self.pure_function = pure_function
    
    def evaluate(self, price_feed: pd.DataFrame, context: StrategyExecutionContext, **kwargs) -> StrategStepEvaluationResult:
        """Evaluate the strategy step.
        
        Args:
            price_feed: Price data
            context: Strategy execution context
            **kwargs: Additional keyword arguments
            
        Returns:
            Strategy step evaluation result
        """
        try:
            result = self._execute_pure_function(price_feed, context, **kwargs)
            self._update_context(context, result, price_feed)
            return StrategStepEvaluationResult(
                is_success=True,
                message="Step completed successfully",
                step_output=result,
                timestamp=price_feed.index[-1]
            )
        except Exception as e:
            return StrategStepEvaluationResult(
                is_success=False,
                message=str(e),
                timestamp=price_feed.index[-1]
            )
    
    def _get_value_from_path(self, obj: Dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation path.
        
        Args:
            obj: Dictionary to get value from
            path: Dot notation path (e.g. "config.trend.min_bars")
            
        Returns:
            Value at path
            
        Raises:
            KeyError: If path is invalid
        """
        current = obj
        for key in path.split('.'):
            if key not in current:
                raise KeyError(f"Path '{path}' not found in object")
            current = current[key]
        return current
    
    def _set_value_in_context(self, context: StrategyExecutionContext, path: str, value: Any) -> None:
        """Set value in context using dot notation path.
        
        Args:
            context: Strategy execution context
            path: Dot notation path (e.g. "result.trend")
            value: Value to set
            
        Raises:
            KeyError: If path is invalid
        """
        # For now, we'll just store everything in the context's step_output
        # This could be enhanced to handle more complex paths
        if not path.startswith('result.'):
            raise KeyError(f"Invalid path for context storage: {path}")
        
        key = path.split('.')[-1]
        context.set_step_output(key, value)

    def _execute_pure_function(self, price_feed: pd.DataFrame, context: StrategyExecutionContext, **kwargs) -> Dict[str, Any]:
        """Execute the pure function with mapped inputs."""
        try:
            # Map context inputs
            context_inputs = {}
            if self.step_config['context_inputs']:
                for param_name, context_path in self.step_config['context_inputs'].items():
                    context_inputs[param_name] = self._get_value_from_path(context, context_path)

            # Map config inputs
            config_inputs = {}
            if self.step_config['config_mapping']:
                for param_name, config_path in self.step_config['config_mapping'].items():
                    config_inputs[param_name] = self._get_value_from_path(kwargs, config_path)

            # Combine all inputs
            all_inputs = {**context_inputs, **config_inputs}

            # Execute pure function
            result = self.pure_function(price_feed, **all_inputs)

            # If result is not a dict, wrap it in a dict with a default key
            if not isinstance(result, dict):
                result = {"result": result}

            return result
        except Exception as e:
            raise ValueError(f"Error in strategy step: {str(e)}")

    def _update_context(self, context: StrategyExecutionContext, result: Dict[str, Any], price_feed: pd.DataFrame) -> None:
        """Update the strategy execution context with the result of the strategy step."""
        from src.models import StrategStepEvaluationResult
        for context_key, result_path in self.step_config['context_outputs'].items():
            try:
                value = self._get_value_from_path(result, result_path)
                # Add result to context using add_result
                result_obj = StrategStepEvaluationResult(
                    is_success=True,
                    message="Step output update",
                    step_output={context_key: value},
                    timestamp=price_feed.index[-1] if not price_feed.empty else None
                )
                context.add_result(result_obj.timestamp, self, result_obj)
            except KeyError as e:
                raise KeyError(f"Failed to update context with key {context_key}: {e}") 