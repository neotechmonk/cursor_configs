

from strategy import StrategyConfig, load_strategy_config


def mock_get_trend():
    """Mock function for testing"""
    pass


def mock_is_extreme_bar(frame_size:int):
    """Mock function for testing"""
    pass


def mock_is_bars_since_extreme_pivot_valid(min_bars, max_bars):
    """Mock function for testing"""
    pass


def mock_is_within_fib_extension():
    """Mock function for testing"""
    pass


def test_load_strategy_config_basic(sample_strategy_config):
    """Test loading a basic strategy configuration"""
    # Load the strategy config
    config = load_strategy_config("test_strategy", str(sample_strategy_config))
    
    # Verify the config object
    assert isinstance(config, StrategyConfig)
    assert config.name == "Test Strategy"
    assert len(config.steps) == 4
    
    # Verify each step
    trend_step = config.steps[0]
    assert trend_step.name == "Detect Trend"
    assert trend_step.config == {}
    
    extreme_step = config.steps[1]
    assert extreme_step.name == "Find Extreme Bar"
    assert extreme_step.config == {"frame_size": 5}
    
    pullback_step = config.steps[2]
    assert pullback_step.name == "Validate Pullback"
    assert pullback_step.config == {"min_bars": 3, "max_bars": 10}
    
    fib_step = config.steps[3]
    assert fib_step.name == "Check Fibonacci Extension"
    assert fib_step.config == {"min_extension": 1.35, "max_extension": 1.875}
    
    # Verify all steps have correct function references
    assert trend_step.evaluation_fn == mock_get_trend
    assert extreme_step.evaluation_fn == mock_is_extreme_bar
    assert pullback_step.evaluation_fn == mock_is_bars_since_extreme_pivot_valid
    assert fib_step.evaluation_fn == mock_is_within_fib_extension
