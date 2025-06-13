"""Tests for strategy configuration loading."""

from pathlib import Path

from src.core.strategy_config import StrategyConfig, load_strategy_config
from src.models.system import StrategyStepTemplate
from tests.mocks.mock_strategy_step_functions import (
    mock_check_fib_wrapper,
    mock_detect_trend_wrapper,
    mock_find_extreme_wrapper,
    mock_validate_pullback_wrapper,
)


def test_load_strategy_config_basic(sample_strategy_config, monkeypatch):
    """Test loading a basic strategy configuration"""
    
    # --- Add project root to sys.path ---
    # This allows import_module in load_strategy_config to find the 'tests' module
    project_root = Path(__file__).parent.parent
    monkeypatch.syspath_prepend(str(project_root))
    # --- End sys.path modification ---

    # Create templates for each step
    trend_template = StrategyStepTemplate(
        system_step_id="detect_trend",
        function="mock.func",
        input_params_map={},
        return_map={},
        config_mapping={}
    )
    
    extreme_template = StrategyStepTemplate(
        system_step_id="find_extreme",
        function="mock.func",
        input_params_map={},
        return_map={},
        config_mapping={}
    )
    
    pullback_template = StrategyStepTemplate(
        system_step_id="validate_pullback",
        function="mock.func",
        input_params_map={},
        return_map={},
        config_mapping={}
    )
    
    fib_template = StrategyStepTemplate(
        system_step_id="check_fib",
        function="mock.func",
        input_params_map={},
        return_map={},
        config_mapping={}
    )

    # Now call the function that performs the import based on YAML strings
    config = load_strategy_config("test_strategy", str(sample_strategy_config))
    
    assert isinstance(config, StrategyConfig)
    assert config.name == "Test Strategy"
    assert len(config.steps) == 4
    
    trend_step = config.steps[0]
    assert trend_step.system_step_id == "detect_trend"
    assert trend_step.description == "Detect Trend"
    assert trend_step.static_config == {}
    assert trend_step.reevaluates == []
    assert trend_step.evaluation_fn.__name__ == mock_detect_trend_wrapper.__name__
    assert trend_step.template == trend_template
    
    extreme_step = config.steps[1]
    assert extreme_step.system_step_id == "find_extreme"
    assert extreme_step.description == "Find Extreme Bar"
    assert extreme_step.static_config == {"frame_size": 5}
    assert extreme_step.reevaluates == []
    assert extreme_step.evaluation_fn.__name__ == mock_find_extreme_wrapper.__name__
    assert extreme_step.template == extreme_template

    pullback_step = config.steps[2]
    assert pullback_step.system_step_id == "validate_pullback"
    assert pullback_step.description == "Validate Pullback"
    assert pullback_step.static_config == {"min_bars": 3, "max_bars": 10}
    assert pullback_step.reevaluates == []
    assert pullback_step.evaluation_fn.__name__ == mock_validate_pullback_wrapper.__name__
    assert pullback_step.template == pullback_template
    
    fib_step = config.steps[3]
    assert fib_step.system_step_id == "check_fib"
    assert fib_step.description == "Check Fibonacci Extension"
    assert fib_step.static_config == {"min_extension": 1.35, "max_extension": 1.875}
    assert len(fib_step.reevaluates) == 1
    # Check reevaluation reference by ID after lookup
    assert fib_step.reevaluates[0].system_step_id == pullback_step.system_step_id 
    assert fib_step.evaluation_fn.__name__ == mock_check_fib_wrapper.__name__
    assert fib_step.template == fib_template

# Context tests are in test_strategy_context.py
