from pathlib import Path

import pytest
from mocks.mock_step_functions import (
    mock_check_fib_wrapper,
    mock_detect_trend_wrapper,
    mock_find_extreme_wrapper,
    mock_validate_pullback_wrapper,
)

from strategy import StrategyConfig, load_strategy_config

# from mock_step_functions import mock_detect_trend_wrapper


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

import pandas as pd  # Keep pandas if needed by fixtures/tests

from strategy import (  # Keep these for tests
    StrategStepEvaluationResult,
    StrategyExecutionContext,
    StrategyStep,
)


@pytest.fixture
def step1() -> StrategyStep:
    # If these tests need specific mock functions, they should be imported from tests.mocks.strategy_mocks
    # Example: from tests.mocks.strategy_mocks import mock_get_trend
    # return StrategyStep(id="step1", name="Step One", ..., evaluation_fn=mock_get_trend, ...)
    # For now, using lambda as it seems sufficient
    return StrategyStep(id="step1", name="Step One", description="", evaluation_fn=lambda p,c,**kw: None, config={}, reevaluates=[])


@pytest.fixture
def step2() -> StrategyStep:
    return StrategyStep(id="step2", name="Step Two", description="", evaluation_fn=lambda p,c,**kw: None, config={}, reevaluates=[])


@pytest.fixture
def step3() -> StrategyStep:
    return StrategyStep(id="step3", name="Step Three", description="", evaluation_fn=lambda p,c,**kw: None, config={}, reevaluates=[])


@pytest.fixture
def ts1() -> pd.Timestamp:
    return pd.Timestamp("2023-01-01 10:00:00")


@pytest.fixture
def ts2() -> pd.Timestamp:
    return pd.Timestamp("2023-01-01 10:01:00")


@pytest.fixture
def ts3() -> pd.Timestamp:
    return pd.Timestamp("2023-01-01 10:02:00")


@pytest.fixture
def ts4() -> pd.Timestamp:
    return pd.Timestamp("2023-01-01 10:03:00")


# --- Context Tests --- 
# (These tests should remain unchanged as they use the fixtures above)

def test_add_result_initial(step1, ts1):
    """Test adding the first result to an empty context."""
    context = StrategyExecutionContext()
    result = StrategStepEvaluationResult(success=True, message="OK", data={"key1": "value1"})
    new_context = context.add_result(ts1, step1, result)
    assert new_context is not context
    assert len(new_context.result_history) == 1
    assert ts1 in new_context.result_history
    assert new_context.result_history[ts1] == (step1, result)
    assert len(context.result_history) == 0


def test_add_result_multiple(step1, step2, ts1, ts2):
    """Test adding multiple distinct results."""
    context = StrategyExecutionContext()
    result1 = StrategStepEvaluationResult(success=True, message="OK1", data={"key1": "value1"})
    result2 = StrategStepEvaluationResult(success=True, message="OK2", data={"key2": "value2"})
    context1 = context.add_result(ts1, step1, result1)
    context2 = context1.add_result(ts2, step2, result2)
    assert len(context2.result_history) == 2
    assert ts1 in context2.result_history
    assert ts2 in context2.result_history
    assert context2.result_history[ts1] == (step1, result1)
    assert context2.result_history[ts2] == (step2, result2)
    assert len(context1.result_history) == 1

# ... other context tests ...


def test_find_latest_successful_data_latest_failed(step1, step2, ts1, ts2):
    """Test finding data when the latest step with the key failed."""
    context = StrategyExecutionContext()
    result1 = StrategStepEvaluationResult(success=True, message="OK1", data={"key1": "value1_ok"})
    result2 = StrategStepEvaluationResult(success=False, message="Fail2", data={"key1": "value2_fail"})
    context = context.add_result(ts1, step1, result1)
    context = context.add_result(ts2, step2, result2)
    found_data = context.find_latest_successful_data("key1")
    assert found_data == "value1_ok"
