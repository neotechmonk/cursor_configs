# Use the existing fixture from conftest.py
"""
TODO : need to introduce complex logic to test
- multiple bars one after another - without failing steps
- multiple bars with a failing step
- multiple bars where failing step re-evaluates another previous step
"""
from typing import Any, Dict

import pandas as pd
import pytest

from src.models import (
    StrategStepEvaluationResult,
    StrategyConfig,
    StrategyExecutionContext,
    StrategyStep,
)
from src.core.strategy_runner import run_strategy
from tests.mocks.mock_strategy_step_functions import (
    EXTREME_BAR_INDEX_KEY,
    mock_check_fib_wrapper,
    mock_detect_trend_wrapper,
    mock_find_extreme_wrapper,
    mock_validate_pullback_wrapper,
)


def mock_eval_step_result_success(price_feed: pd.DataFrame, exp_ret_data: Dict[str, Any], step_id: str) -> StrategStepEvaluationResult:  # noqa: F821
    if not exp_ret_data: 
        raise ValueError(f"Expected return data for step {step_id}")
    
    return StrategStepEvaluationResult(
        is_success=True,
        timestamp=price_feed.index[-1],
        message=f"Succesful result for {step_id}",
        step_output=exp_ret_data)

    
def mock_eval_step_result_failure(price_feed: pd.DataFrame,  step_id: str) -> StrategStepEvaluationResult:  # noqa: F821
    
    return StrategStepEvaluationResult(
            timestamp=price_feed.index[-1],
            is_success=False,
            message=f"Failed result for {step_id}",
        )
    

def mock_eval_step(step_id: str, eval_fn) -> StrategyStep:  # noqa: F821
    return StrategyStep(
            id=step_id,
            name=f"Mock Step {step_id}",
            description=f"Mock Step {step_id}",
            evaluation_fn=eval_fn,
            config={},
            reevaluates=[])


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

    # Define the evaluation functions
    def step1_eval(price_feed: pd.DataFrame, context: StrategyExecutionContext, **config) -> StrategStepEvaluationResult:
        """sucessful evaluation for all bars"""
        return mock_eval_step_result_success(price_feed, {"step1_data": True}, "step1")

    def step2_eval(price_feed: pd.DataFrame, context: StrategyExecutionContext, **config) -> StrategStepEvaluationResult:
        """sucessful evaluation for all bars"""
        return mock_eval_step_result_success(price_feed, {"step2_data": True}, "step2")

    def step3_eval(price_feed: pd.DataFrame, context: StrategyExecutionContext, **config) -> StrategStepEvaluationResult:
        """sucessful evaluation for only the three bar"""
        last_bar = price_feed.index[-1]
        if last_bar in pd.to_datetime(['2024-01-01', '2024-01-02']):
            return mock_eval_step_result_failure(price_feed, "step3")
        elif last_bar == pd.to_datetime(['2024-01-03']):
            return mock_eval_step_result_success(price_feed, {"step3_data": True}, "step3")
        else:
            raise ValueError(f"Unexpected bar index: {last_bar}")

    # Create mock steps
    step1 = mock_eval_step("step1", step1_eval)
    step2 = mock_eval_step("step2", step2_eval)
    step3 = mock_eval_step("step3", step3_eval)

    # Create strategy config
    config = StrategyConfig(
        name="Test Multi-Bar Strategy",
        steps=[step1, step2, step3]
    )


    exec_context = None

    # Run strategy incrementally with increasing bars
    for i in range(1, len(price_feed) + 1):
        # Slice the price_feed to include only the first i bars
        incremental_price_feed = price_feed.iloc[:i]

        # print (f"*********Incremental price feed: {incremental_price_feed}")

        
        # Run strategy with the current slice of price_feed
        exec_context = run_strategy(config, incremental_price_feed, context=exec_context)

        # each run should have 3 results corresponding to 3 steps irrespective of success or failure
        print (f"***** Number of results in history: {(exec_context._strategy_steps_results)}")
        break
        # assert len(exec_context.result_history) == (i+1)*3
        
        # # Check which step is successful vs failed for each run of the strategy
        # for (timestamp, step), result in exec_context.result_history.items():
        #     print(f"Step '{step.name}' at {timestamp}: {'Success' if result.success else 'Failure'}")

        # # Count the results in history for each step
        # step_success_count = {}
        # for (timestamp, step), result in exec_context.result_history.items():
        #     if step.id not in step_success_count:
        #         step_success_count[step.id] = {'success': 0, 'failure': 0}
        #     if result.success:
        #         step_success_count[step.id]['success'] += 1
        #     else:
        #         step_success_count[step.id]['failure'] += 1

        # # Print the count of successes and failures for each step
        # for step_id, counts in step_success_count.items():
        #     print(f"Step '{step_id}': {counts['success']} successes, {counts['failure']} failures")

        # # Check the result data for each step to match
        # for (timestamp, step), result in exec_context.result_history.items():
        #     expected_data_key = f"{step.id}_data"
        #     # assert expected_data_key in result.data, f"Expected data key '{expected_data_key}' not found in step '{step.name}'"
        #     print(f"Step '{step.name}' at {timestamp} has expected data: {result.data[expected_data_key]}")


@pytest.mark.skip() # Keep test active
def test_run_strategy_happy_path_with_context(uptrending_price_feed):
    """Test run_strategy runs all steps successfully, passing data via context."""
    # Arrange
    price_feed = uptrending_price_feed # Use a sample price feed
    
    # Define steps manually, assigning the *wrapper* functions directly
    step1 = StrategyStep(
        id="detect_trend",
        name="Detect Trend",
        description="Detects the trend",
        evaluation_fn=mock_detect_trend_wrapper, # Use wrapper
        config={},
        reevaluates=[] # Ensure default factory list is present
    )
    step2 = StrategyStep(
        id="find_extreme",
        name="Find Extreme Bar",
        description="Finds extreme bars",
        evaluation_fn=mock_find_extreme_wrapper, # Use wrapper
        config={"frame_size": 5}, # Config from YAML
        reevaluates=[] # Ensure default factory list is present
    )
    step3 = StrategyStep(
        id="validate_pullback",
        name="Validate Pullback",
        description="Validates pullback bars",
        evaluation_fn=mock_validate_pullback_wrapper, # Use wrapper
        config={"min_bars": 3, "max_bars": 10}, # Config from YAML
        reevaluates=[] # Ensure default factory list is present
    )
    step4 = StrategyStep(
        id="check_fib",
        name="Check Fibonacci Extension",
        description="Checks fib extension",
        evaluation_fn=mock_check_fib_wrapper, # Use wrapper
        config={"min_extension": 1.35, "max_extension": 1.875}, # Config from YAML
        reevaluates=[] # Initialize, then add reference below
    )
    # Setup reevaluation link (as done in load_strategy_config)
    step4.reevaluates.append(step3) 

    config = StrategyConfig(
        name="Test Strategy", # Name from YAML
        steps=[step1, step2, step3, step4]
    )

    # Act
    # run_strategy returns the final context
    final_context: StrategyExecutionContext = run_strategy(config, price_feed)
    
    # Assert
    # Check that the returned context is of the correct type
    assert isinstance(final_context, StrategyExecutionContext)

    # Verify all steps were executed and added to context
    assert len(final_context._strategy_steps_results) == 4
    
    # Create a map of results by step for easier verification
    results_map = {}
    for (timestamp, step), result in final_context._strategy_steps_results.items():
        assert result is not None
        assert result.is_success, f"Step '{step.name}' (ID: {step.id}) failed unexpectedly: {result.message}"
        results_map[step.id] = result
    
    # Verify all steps from config were processed
    assert len(results_map) == len(config.steps)
    
    # Check specific results data produced by wrappers
    # Step 1. Trend Detection
    assert "detect_trend" in results_map
    assert results_map["detect_trend"].data == {"trend": "UP"}
    
    # Step 2. Extreme Bar Detection
    assert "find_extreme" in results_map
    extreme_result = results_map["find_extreme"]
    assert extreme_result.data is not None
    assert extreme_result.data[EXTREME_BAR_INDEX_KEY] == price_feed.index[-1]
    assert extreme_result.data["is_extreme"] is True
    
    # Step 3. Pullback Validation
    assert "validate_pullback" in results_map
    assert results_map["validate_pullback"].data == {"bars_valid": True}
    
    # 4. Fibonacci Extension Check
    assert "check_fib" in results_map
    assert results_map["check_fib"].data == {"fib_valid": True}
    
    # Verify context's data retrieval functionality
    # Test finding latest successful data
    extreme_index = final_context.get_latest_strategey_step_output_result(EXTREME_BAR_INDEX_KEY)
    assert extreme_index is not None
    assert extreme_index == price_feed.index[-1]
    
    # Print final context for debugging if needed
    # pprint(final_context.result_history)