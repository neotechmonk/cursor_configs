
# Use the existing fixture from conftest.py
from executor import StrategyExecutor

from strategy import load_strategy_config


def test_executor_happy_path(sample_strategy_config, uptrending_price_feed):
    """Test the executor runs all steps successfully in a happy path scenario."""
    # Arrange
    config = load_strategy_config("test_strategy", str(sample_strategy_config))
    executor = StrategyExecutor(config)
    price_feed = uptrending_price_feed # Use a sample price feed
    
    # Act
    executor.run(price_feed)
    
    # Assert
    execution_log = executor.get_all_results()
    
    assert len(execution_log) == 4 # All steps should be in the log
    
    # Check each step was executed successfully
    for record in execution_log:
        assert record.executed
        assert record.result is not None
        assert record.result.success
        print(f"Step '{record.step.name}' Result: {record.result}") # Optional: print results for debugging

    # Check specific results (optional, based on mock function behavior)
    trend_result = executor.get_step_result("detect_trend")
    assert trend_result.data == {"trend": "UP"}
    
    extreme_result = executor.get_step_result("find_extreme")
    assert extreme_result.data == {"is_extreme": True}
    
    pullback_result = executor.get_step_result("validate_pullback")
    assert pullback_result.data == {"bars_valid": True}

    fib_result = executor.get_step_result("check_fib")
    assert fib_result.data == {"fib_valid": True} 