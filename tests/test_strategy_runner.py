# Use the existing fixture from conftest.py
"""
TODO : need to introduce complex logic to test
- multiple bars one after another - without failing steps
- multiple bars with a failing step
- multiple bars where failing step re-evaluates another previous step
"""
from pprint import pprint

from src.models import StrategyConfig, StrategyExecutionContext, StrategyStep
from src.strategy_runner import run_strategy
from tests.mocks.mock_strategy_step_functions import (
    EXTREME_BAR_INDEX_KEY,
    mock_check_fib_wrapper,
    mock_detect_trend_wrapper,
    mock_find_extreme_wrapper,
    mock_validate_pullback_wrapper,
)


# @pytest.mark.skip() # Keep test active
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
    assert len(final_context.result_history) == 4
    
    # Create a map of results by step for easier verification
    results_map = {}
    for (timestamp, step), result in final_context.result_history.items():
        assert result is not None
        assert result.success, f"Step '{step.name}' (ID: {step.id}) failed unexpectedly: {result.message}"
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
    extreme_index = final_context.find_latest_successful_data(EXTREME_BAR_INDEX_KEY)
    assert extreme_index is not None
    assert extreme_index == price_feed.index[-1]
    
    
    # Print final context for debugging if needed
    # pprint(final_context.result_history)