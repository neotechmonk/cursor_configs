"""
Tests for the strategy runner functionality.
Tests cover:
- Multiple bars execution without failing steps
- Multiple bars with failing steps
- Multiple bars with step reevaluation
- Context management and data passing
"""
from typing import Any, Dict

import pandas as pd
import pytest

from src.core.strategy_runner import run_strategy
from src.models import (
    StrategyConfig,
    StrategyExecutionContext,
    StrategyStep,
    StrategyStepEvaluationResult,
    StrategyStepTemplate,
)
from tests.mocks.mock_strategy_step_functions import (
    step1_wrapper,
    step2_wrapper,
    step3_wrapper,
)


def mock_eval_step(step_id: str, eval_fn) -> StrategyStep:
    """Create a mock strategy step for testing.
    
    Args:
        step_id: The system step ID
        eval_fn: The evaluation function to use
        
    Returns:
        A StrategyStep instance
    """
    template = StrategyStepTemplate(
        system_step_id=step_id,
        function=f"tests.mocks.mock_strategy_step_functions.{step_id}_wrapper",
        input_params_map={},
        return_map={},
        config_mapping={}
    )
    
    return StrategyStep(
        system_step_id=step_id,
        description=f"Mock Step {step_id}",
        evaluation_fn=eval_fn,
        static_config={},
        dynamic_config={},
        reevaluates=[],
        template=template
    )


def test_run_strategy_with_multiple_bars():
    """Test strategy execution over multiple bars where:
    - first bar succeeds in step 1 and step 2
    - second bar is the same as first bar
    - third bar succeeds all three steps
    """
    # Create test data with multiple bars
    dates = pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
    price_feed = pd.DataFrame({
        'open': [100, 101, 102],
        'high': [102, 103, 104],
        'low': [99, 100, 101],
        'close': [101, 102, 103]
    }, index=dates)

    # Create mock steps using the wrapper functions
    step1 = mock_eval_step("step1", step1_wrapper)
    step2 = mock_eval_step("step2", step2_wrapper)
    step3 = mock_eval_step("step3", step3_wrapper)

    # Create strategy config
    config = StrategyConfig(
        name="Test Multi-Bar Strategy",
        steps=[step1, step2, step3]
    )

    exec_context = None
    step_success_count = {}

    # Run strategy incrementally with increasing bars
    for i in range(1, len(price_feed) + 1):
        # Reset success count for this iteration
        step_success_count = {step_id: {'success': 0, 'failure': 0} for step_id in ['step1', 'step2', 'step3']}
        
        # Slice the price_feed to include only the first i bars
        incremental_price_feed = price_feed.iloc[:i]

        # Run strategy with the current slice of price_feed
        exec_context = run_strategy(config, incremental_price_feed, context=exec_context)

        # Count successes and failures for each step in this iteration only
        for (timestamp, step), result in exec_context.strategy_steps_results.items():
            if result.is_success:
                step_success_count[step.system_step_id]['success'] += 1
            else:
                step_success_count[step.system_step_id]['failure'] += 1

        # Verify results for this iteration
        if i == 1:  # First bar
            assert step_success_count['step1']['success'] == 1
            assert step_success_count['step2']['success'] == 1
            assert step_success_count['step3']['success'] == 0
        elif i == 2:  # Second bar
            assert step_success_count['step1']['success'] == 1
            assert step_success_count['step2']['success'] == 1
            assert step_success_count['step3']['success'] == 0
        else:  # Third bar
            assert step_success_count['step1']['success'] == 1
            assert step_success_count['step2']['success'] == 1
            assert step_success_count['step3']['success'] == 1


def test_run_strategy_all_success():
    """Test strategy execution over multiple bars where all steps succeed."""
    # Create test data
    dates = pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
    price_feed = pd.DataFrame({
        'open': [100, 101, 102],
        'high': [102, 103, 104],
        'low': [99, 100, 101],
        'close': [101, 102, 103]
    }, index=dates)

    # Create steps using the wrapper functions
    step1 = mock_eval_step("step1", step1_wrapper)
    step2 = mock_eval_step("step2", step2_wrapper)
    step3 = mock_eval_step("step3", step3_wrapper)

    config = StrategyConfig(
        name="Test All Success Strategy",
        steps=[step1, step2, step3]
    )

    exec_context = None
    step_success_count = {}

    # Run strategy for all bars
    for i in range(1, len(price_feed) + 1):
        # Reset success count for this iteration
        step_success_count = {step_id: {'success': 0, 'failure': 0} for step_id in ['step1', 'step2', 'step3']}
        
        incremental_price_feed = price_feed.iloc[:i]
        exec_context = run_strategy(config, incremental_price_feed, context=exec_context)

        # Count successes for this iteration only
        for (timestamp, step), result in exec_context.strategy_steps_results.items():
            if result.is_success:
                step_success_count[step.system_step_id]['success'] += 1
            else:
                step_success_count[step.system_step_id]['failure'] += 1

        # Verify all steps succeeded for this bar
        for step_id in ['step1', 'step2', 'step3']:
            if step_id == 'step3' and i < 3:
                assert step_success_count[step_id]['success'] == 0
            else:
                assert step_success_count[step_id]['success'] == 1
            assert step_success_count[step_id]['failure'] == 0


def test_run_strategy_with_reevaluation():
    """Test strategy execution with step reevaluation."""
    # Create test data
    dates = pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
    price_feed = pd.DataFrame({
        'open': [100, 101, 102],
        'high': [102, 103, 104],
        'low': [99, 100, 101],
        'close': [101, 102, 103]
    }, index=dates)

    # Create steps using the wrapper functions
    step1 = mock_eval_step("step1", step1_wrapper)
    step2 = mock_eval_step("step2", step2_wrapper)
    step3 = mock_eval_step("step3", step3_wrapper)
    
    # Setup reevaluation relationships
    step2.reevaluates.append(step1)
    step3.reevaluates.extend([step1, step2])

    config = StrategyConfig(
        name="Test Reevaluation Strategy",
        steps=[step1, step2, step3]
    )

    exec_context = None
    step_success_count = {}

    # Run strategy for all bars
    for i in range(1, len(price_feed) + 1):
        # Reset success count for this iteration
        step_success_count = {step_id: {'success': 0, 'failure': 0} for step_id in ['step1', 'step2', 'step3']}
        
        incremental_price_feed = price_feed.iloc[:i]
        exec_context = run_strategy(config, incremental_price_feed, context=exec_context)

        # Count successes for this iteration only
        for (timestamp, step), result in exec_context.strategy_steps_results.items():
            if result.is_success:
                step_success_count[step.system_step_id]['success'] += 1
            else:
                step_success_count[step.system_step_id]['failure'] += 1

        # Verify results for this iteration
        if i == 1:  # First bar
            assert step_success_count['step1']['success'] == 1
            assert step_success_count['step2']['success'] == 1
            assert step_success_count['step3']['success'] == 0
        elif i == 2:  # Second bar
            assert step_success_count['step1']['success'] == 1
            assert step_success_count['step2']['success'] == 1
            assert step_success_count['step3']['success'] == 0
        else:  # Third bar
            assert step_success_count['step1']['success'] == 1
            assert step_success_count['step2']['success'] == 1
            assert step_success_count['step3']['success'] == 1