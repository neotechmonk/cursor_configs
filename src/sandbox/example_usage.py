"""Example usage of the pipeline configuration pattern."""

import os
from datetime import datetime, timedelta

import pandas as pd

from src.core.strategy_config import load_strategy_config
from src.core.strategy_runner import run_strategy
from src.models import StrategyExecutionContext
from src.models.base import Direction, PriceLabel

from .pipeline_config import PipelineConfig
from .strategy_step import StrategyStep
from .strategy_step_factory import StrategyStepFactory


def main():
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'strategy_steps.yaml')
    pipeline_config = PipelineConfig(config_path)
    
    # Create factory
    factory = StrategyStepFactory(pipeline_config)
    
    # Create steps
    steps = {}
    for step_name in pipeline_config.get_all_step_names():
        step_config = pipeline_config.get_step_config(step_name)
        pure_function = StrategyStepFactory.load_pure_function(step_config['pure_function'])
        steps[step_name] = factory.create_step(step_name, pure_function)
    
    # Create example price feed with realistic data
    dates = pd.date_range(start=datetime.now(), periods=100, freq='1min')
    price_feed = pd.DataFrame({
        PriceLabel.OPEN: [100 + i for i in range(100)],
        PriceLabel.HIGH: [105 + i for i in range(100)],
        PriceLabel.LOW: [95 + i for i in range(100)],
        PriceLabel.CLOSE: [102 + i for i in range(100)]
    }, index=dates)
    
    # Create context and config matching trend_following.yaml
    context = StrategyExecutionContext()
    config = {
        'extreme': {'frame_size': 5},
        'pullback': {'min_bars': 3, 'max_bars': 10},
        'fib': {
            'min_extension': 1.35,
            'max_extension': 1.875
        }
    }
    
    # Execute steps in order
    for step_name, step in steps.items():
        print(f"\nExecuting step: {step_name}")
        result = step.evaluate(price_feed, context, **config)
        if not result.is_success:
            print(f"Step {step_name} failed: {result.message}")
            break
        print(f"Step {step_name} succeeded: {result.message}")
        print(f"Step output: {result.step_output}")
        
        # Store current bar index for fib calculation
        if step_name == 'find_extreme':
            context.set_step_output('current_bar_index', price_feed.index[-1])

    # Compare with actual strategy runner
    print("\n\nRunning with actual strategy runner:")
    strategy_config = load_strategy_config('trend_following')
    final_context, history_log, executed_steps = run_strategy(strategy_config, price_feed)
    
    print("\nStrategy runner results:")
    for step, result in executed_steps:
        print(f"Step {step.name}: {result.message}")
        print(f"Output: {result.step_output}")

if __name__ == '__main__':
    main() 