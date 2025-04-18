from pathlib import Path

import pandas as pd  # Keep pandas if needed by fixtures/tests
import pytest
from mocks.mock_step_functions import (
    mock_check_fib_wrapper,
    mock_detect_trend_wrapper,
    mock_find_extreme_wrapper,
    mock_validate_pullback_wrapper,
)

from strategy import (  # Keep these for tests
    StrategStepEvaluationResult,
    StrategyConfig,
    StrategyExecutionContext,
    StrategyStep,
    load_strategy_config,
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

# --- Tests for StrategyExecutionContext ---
# Moved to tests/test_strategy_context.py

# Remove fixtures that were moved
# @pytest.fixture
# def step1() -> StrategyStep:
#     ...

# @pytest.fixture
# def step2() -> StrategyStep:
#     ...

# @pytest.fixture
# def step3() -> StrategyStep:
#     ...

# @pytest.fixture
# def ts1() -> pd.Timestamp:
#     ...

# @pytest.fixture
# def ts2() -> pd.Timestamp:
#     ...

# @pytest.fixture
# def ts3() -> pd.Timestamp:
#     ...

# @pytest.fixture
# def ts4() -> pd.Timestamp:
#     ...


# --- REMOVE MOVED Context Tests --- 
# def test_add_result_initial(step1, ts1):
#     ...

# def test_add_result_multiple(step1, step2, ts1, ts2):
#     ...

# Keep other context tests if they exist
# def test_add_result_no_data(step1, step2, ts1, ts2):
#     ...
# def test_add_result_duplicate_data_different_steps_raises(step1, step2, ts1, ts2):
#     ...
# def test_add_result_duplicate_data_same_step_allowed(step1, ts1, ts2):
#     ...
# def test_find_latest_successful_data_empty():
#     ...
# def test_find_latest_successful_data_not_found(step1, ts1):
#     ...
# def test_find_latest_successful_data_single_success(step1, ts1):
#     ...
# def test_find_latest_successful_data_multiple_one_success(step1, step2, ts1, ts2):
#     ...
# def test_find_latest_successful_data_multiple_success_returns_latest(step1, step2, step3, ts1, ts2, ts3):
#     ...
# def test_find_latest_successful_data_latest_failed(step1, step2, ts1, ts2):
#     ...

# Remove imports only needed by moved tests/fixtures if they aren't used by remaining tests
# from dataclasses import dataclass
# import pandas as pd 
