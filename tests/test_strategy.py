from pathlib import Path

from strategy import load_strategy_config

from strategy_config import StrategyConfig
from tests.mocks.mock_strategy_step_functions import (
    mock_check_fib_wrapper,
    mock_detect_trend_wrapper,
    mock_find_extreme_wrapper,
    mock_validate_pullback_wrapper,
)


#
def test_load_strategy_config_basic(sample_strategy_config, monkeypatch):
    """Test loading a basic strategy configuration"""
    
    # --- Add project root to sys.path ---
    # This allows import_module in load_strategy_config to find the 'tests' module
    project_root = Path(__file__).parent.parent
    monkeypatch.syspath_prepend(str(project_root))
    # --- End sys.path modification ---

    # Now call the function that performs the import based on YAML strings
    config = load_strategy_config("test_strategy", str(sample_strategy_config))
    
    assert isinstance(config, StrategyConfig)
    assert config.name == "Test Strategy"
    assert len(config.steps) == 4
    
    trend_step = config.steps[0]
    assert trend_step.id == "detect_trend"
    assert trend_step.name == "Detect Trend"
    assert trend_step.config == {}
    assert trend_step.reevaluates == []
    assert trend_step.evaluation_fn.__name__ == mock_detect_trend_wrapper.__name__
    
    extreme_step = config.steps[1]
    assert extreme_step.id == "find_extreme"
    assert extreme_step.name == "Find Extreme Bar"
    assert extreme_step.config == {"frame_size": 5}
    assert extreme_step.reevaluates == []
    assert extreme_step.evaluation_fn.__name__ == mock_find_extreme_wrapper.__name__

    pullback_step = config.steps[2]
    assert pullback_step.id == "validate_pullback"
    assert pullback_step.name == "Validate Pullback"
    assert pullback_step.config == {"min_bars": 3, "max_bars": 10}
    assert pullback_step.reevaluates == []
    assert pullback_step.evaluation_fn.__name__ == mock_validate_pullback_wrapper.__name__
    
    fib_step = config.steps[3]
    assert fib_step.id == "check_fib"
    assert fib_step.name == "Check Fibonacci Extension"
    assert fib_step.config == {"min_extension": 1.35, "max_extension": 1.875}
    assert len(fib_step.reevaluates) == 1
    # Check reevaluation reference by ID after lookup
    assert fib_step.reevaluates[0].id == pullback_step.id 
    assert fib_step.evaluation_fn.__name__ == mock_check_fib_wrapper.__name__
    
    assert trend_step.evaluation_fn.__name__ == "mock_detect_trend_wrapper" 
    assert extreme_step.evaluation_fn.__name__ == "mock_find_extreme_wrapper"
    assert pullback_step.evaluation_fn.__name__ == "mock_validate_pullback_wrapper"
    assert fib_step.evaluation_fn.__name__ == "mock_check_fib_wrapper"

# Context tests are in test_strategy_context.py
