# Use the existing fixture from conftest.py

# Import functions and classes from strategy module

# Import the *wrapper* functions needed for this test
from mocks.mock_step_functions import (
    EXTREME_BAR_INDEX_KEY,  # Also import the key if needed here
    mock_check_fib_wrapper,
    mock_detect_trend_wrapper,
    mock_find_extreme_wrapper,
    mock_validate_pullback_wrapper,
)

from src.models import StrategStepEvaluationResult
from src.strategy import (  # load_strategy_config, # No longer needed for this specific test
    StrategyConfig,  # Import StrategyConfig
    StrategyExecutionContext,
    StrategyStep,  # Import needed for type hints
    run_strategy,
)


# @pytest.mark.skip() # Keep test active
def test_run_strategy_happy_path_with_context(uptrending_price_feed):
    """Test run_strategy runs all steps successfully, passing data via context."""
    # Arrange
    price_feed = uptrending_price_feed # Use a sample price feed

    # ---- Manually construct config for test ----
    # This avoids the import_module issue entirely within the test context.
    
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

    # from src.strategy import StrategyConfig # Import if not already done (imported above)
    config = StrategyConfig(
        name="Test Strategy", # Name from YAML
        steps=[step1, step2, step3, step4]
    )
    # ---- End Manually construct config ----

    # Act
    # run_strategy now returns the final context, the full history log, and the list of results from this run
    final_context, full_history, executed_results = run_strategy(config, price_feed)
    
    # Assert
    assert isinstance(final_context, StrategyExecutionContext)
    # executed_results is List[Tuple[StrategyStep, StrategStepEvaluationResult]]
    assert len(executed_results) == 4 # All 4 steps should have been executed and returned
    
    # Check each step result was successful
    results_map = {} # Store results by ID for easier lookup
    for step, result in executed_results:
        assert result is not None
        assert result.success, f"Step '{step.name}' (ID: {step.id}) failed unexpectedly: {result.message}"
        print(f"Step '{step.name}' Result: {result}") # Optional: print results
        results_map[step.id] = result
        
    # Verify all steps from config were processed
    assert len(results_map) == len(config.steps)

    # Check specific results data produced by wrappers (which call pure functions)
    assert "detect_trend" in results_map
    assert results_map["detect_trend"].data == {"trend": "UP"} # From mock_pure_get_trend via wrapper
    
    assert "find_extreme" in results_map
    # Check data placed into context by the wrapper (using EXTREME_BAR_INDEX_KEY)
    assert results_map["find_extreme"].data is not None
    # from tests.mock_step_functions import EXTREME_BAR_INDEX_KEY # No longer need separate import here
    assert results_map["find_extreme"].data.get(EXTREME_BAR_INDEX_KEY) == price_feed.index[-1] # Wrapper puts index under this key
    assert results_map["find_extreme"].data.get("is_extreme") is True # Wrapper should also pass this through
    
    assert "validate_pullback" in results_map
    # Wrapper calls pure function which returns this
    assert results_map["validate_pullback"].data == {"bars_valid": True} 

    assert "check_fib" in results_map
    # Wrapper calls pure function which returns this
    assert results_map["check_fib"].data == {"fib_valid": True}

    # Verify context history (keyed by timestamp)
    assert len(final_context.result_history) == 4 # History should contain 4 entries (one per step execution)
    
    # Example check: Find the data added by 'find_extreme' using the context
    extreme_index = final_context.find_latest_successful_data(EXTREME_BAR_INDEX_KEY)
    assert extreme_index is not None
    assert extreme_index == price_feed.index[-1]
    
    trend = final_context.find_latest_successful_data("trend")
    assert trend == "UP"

    # You can add more specific checks on the full_history log if needed
    assert len(full_history) == 4
    
    # # Check each step result was successful
    # results_map = {} # Store results by ID for easier lookup
    # for step, result in execution_results:
    #     assert result is not None
    #     assert result.success, f"Step '{step.name}' failed unexpectedly: {result.message}"
    #     print(f"Step '{step.name}' Result: {result}") # Optional: print results
    #     results_map[step.id] = result
        
    # # Verify all steps from config were processed
    # assert len(results_map) == len(config.steps)

    # # Check specific results data produced by wrappers
    # assert "detect_trend" in results_map
    # assert results_map["detect_trend"].data == {"trend": "UP"}
    
    # assert "find_extreme" in results_map
    # Check that the wrapper produced the correct key and included original data
    # assert EXTREME_BAR_INDEX_KEY in results_map["find_extreme"].data
    # assert results_map["find_extreme"].data["is_extreme"] == True
    # assert results_map["find_extreme"].data[EXTREME_BAR_INDEX_KEY] == price_feed.index[-1] # Verify index output
    
    # assert "validate_pullback" in results_map
    # assert results_map["validate_pullback"].data == {"bars_valid": True}

    # assert "check_fib" in results_map
    # assert results_map["check_fib"].data == {"fib_valid": True}

    # # Verify context history
    # assert len(final_context.results_history) == 4 # History for 4 steps
    # assert len(final_context.get_step_history("detect_trend")) == 1
    # assert final_context.get_step_history("detect_trend")[0].success == True
    # ... (can add more context checks if needed) ... 