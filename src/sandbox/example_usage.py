"""Example usage of the strategy step evaluation pattern."""

import os
from datetime import datetime
from typing import Dict

import pandas as pd
import yaml

from src.models import (
    StrategStepEvaluationResult,
    StrategyExecutionContext,
    StrategyStep,
)
from src.models.base import PriceLabel
from src.sandbox.evaluator import StepEvaluator
from src.sandbox.models import StrategyStepRegistry
from tests.mocks.mock_pure_logic import (
    mock_pure_get_trend,
    mock_pure_is_bars_since_extreme_pivot_valid,
    mock_pure_is_extreme_bar,
    mock_pure_is_within_fib_extension,
)

# Always resolve path relative to this file

# Map step names to their mock functions
STEP_MOCKS = {
    "detect_trend": lambda price_feed, **kwargs: {"result": mock_pure_get_trend(price_feed, **kwargs)},
    "find_extreme": lambda price_feed, **kwargs: {"result": mock_pure_is_extreme_bar(price_feed, trend=kwargs.get('trend'), **kwargs)},
    "validate_pullback": lambda price_feed, **kwargs: {"result": mock_pure_is_bars_since_extreme_pivot_valid(price_feed, extreme_bar_index=kwargs.get('extreme_bar_index'), **kwargs)},
    "check_fib": lambda price_feed, **kwargs: {"result": mock_pure_is_within_fib_extension(price_feed, **kwargs)}
}


def load_strategy_config(strategy_name: str = "trend_following") -> Dict:
    """Load strategy configuration from YAML file.
    
    Args:
        strategy_name: Name of the strategy to load (default: "trend_following")
        
    Returns:
        Dictionary containing the strategy configuration
        
    Raises:
        FileNotFoundError: If the strategy configuration file doesn't exist
        yaml.YAMLError: If the YAML file is invalid
    """
    config_path = os.path.join("configs", "strategies", f"{strategy_name}.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Strategy configuration file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    try:
        # Load strategy configuration
        strategy_config = load_strategy_config()
        print(f"\nLoaded strategy: {strategy_config['name']}")
        print("Steps:")
        for step in strategy_config['steps']:
            print(f"- {step['name']} (ID: {step['id']})")
            if step.get('reevaluates'):
                print(f"  Reevaluates: {step['reevaluates']}")
        
        # Load step registry using from_yaml method
        registry = StrategyStepRegistry.from_yaml()
        print(f"\nLoaded registry with {len(registry.steps)} steps:")
        for step_name in registry.step_template_names:
            print(f"- {step_name}")
        
        # Create example price feed with realistic data
        dates = pd.date_range(start=datetime.now(), periods=100, freq='1min')
        price_feed = pd.DataFrame({
            PriceLabel.OPEN: [100 + i for i in range(100)],
            PriceLabel.HIGH: [105 + i for i in range(100)],
            PriceLabel.LOW: [95 + i for i in range(100)],
            PriceLabel.CLOSE: [102 + i for i in range(100)]
        }, index=dates)
        
        # Create context and config from strategy configuration
        context = StrategyExecutionContext()
        config = {
            step['id']: step.get('config', {})
            for step in strategy_config['steps']
        }
        print("\nStrategy configuration:")
        for step_id, step_config in config.items():
            print(f"- {step_id}: {step_config}")
        
        # Execute steps in order
        for step in strategy_config['steps']:
            step_name = step['id']
            print(f"\nExecuting step: {step_name}")
            
            # Get step template and create evaluator
            step_template = registry.get_step_template(step_name)
            evaluator = StepEvaluator(step_template, STEP_MOCKS[step_name])
            
            # Execute step
            result = evaluator.evaluate(price_feed, context, **config)
            if not result.is_success:
                print(f"Step {step_name} failed: {result.message}")
                break
                
            print(f"Step {step_name} succeeded: {result.message}")
            print(f"Step output: {result.step_output}")
            
            # Add result to context for future steps
            dummy_step = StrategyStep(
                id=f"{step_name}_{price_feed.index[-1]}",
                name=step['name'],
                evaluation_fn=lambda *a, **k: StrategStepEvaluationResult(),
                config=step.get('config', {}),
                description=step.get('description'),
                reevaluates=[]  # TODO: Handle reevaluates from config
            )
            context.add_result(price_feed.index[-1], dummy_step, result)
                
    except Exception as e:
        print(f"Error loading strategy configuration: {str(e)}")
        import traceback
        print("\nFull error traceback:")
        print(traceback.format_exc())

if __name__ == '__main__':
    main() 