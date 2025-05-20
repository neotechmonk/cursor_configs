"""Factory for creating strategy steps."""

import importlib
import inspect
from typing import Any, Callable, Dict

from .pipeline_config import PipelineConfig
from .strategy_step import StrategyStep


class StrategyStepFactory:
    """Factory for creating strategy steps from configuration."""
    
    def __init__(self, config: PipelineConfig):
        """Initialize factory with pipeline configuration.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
    
    def create_step(self, step_name: str, pure_function: Callable) -> StrategyStep:
        """Create a strategy step.
        
        Args:
            step_name: Name of the step to create
            pure_function: The pure function to execute
            
        Returns:
            Configured strategy step
            
        Raises:
            KeyError: If step_name is not found in configuration
            ValueError: If pure_function signature doesn't match configuration
        """
        step_config = self.config.get_step_config(step_name)
        
        # Validate pure function signature
        self._validate_function_signature(pure_function, step_config)
        
        return StrategyStep(step_config, pure_function)
    
    def _validate_function_signature(self, pure_function: Callable, step_config: Dict[str, Any]) -> None:
        """Validate that the pure function has the required parameters."""
        sig = inspect.signature(pure_function)
        required_params = set(sig.parameters.keys()) - {'price_feed'}

        # Map context keys to function parameters
        context_mapping = {
            'extreme_bar_index': 'major_swing_high_idx',
            # Add more mappings if needed
        }

        for context_key in step_config['context_inputs'].keys():
            mapped_key = context_mapping.get(context_key, context_key)
            if mapped_key not in required_params:
                raise ValueError(f"Pure function missing required parameter from context: {context_key}")

        for config_key in step_config['config_mapping'].keys():
            if config_key not in required_params:
                raise ValueError(f"Pure function missing required parameter from config: {config_key}")
    
    @classmethod
    def load_pure_function(cls, function_path: str) -> Callable:
        """Load a pure function from a module path.
        
        Args:
            function_path: Path to function (e.g. "src.utils.mock_pure_get_trend")
            
        Returns:
            The loaded function
            
        Raises:
            ImportError: If function cannot be loaded
        """
        module_path, function_name = function_path.rsplit('.', 1)
        try:
            module = importlib.import_module(module_path)
            return getattr(module, function_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to load function {function_path}: {e}") 