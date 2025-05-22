from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.models import StrategyExecutionContext
from src.sandbox.models import StrategyStepTemplate
from src.sandbox.strategy_step_evaluator import (
    StepEvaluator,
    get_value_from_path,
    map_strategy_step_function_results,
    prep_arguments_for_strategy_step_function,
)


# region: get_value_from_path
def test_get_value_from_path_simple_key():
    """Should return value for a simple key."""
    obj = {"a": 1}
    assert get_value_from_path(obj, "a") == 1


def test_get_value_from_path_nested_key():
    """Should return value for a nested key path."""
    obj = {"a": {"b": {"c": 42}}}
    assert get_value_from_path(obj, "a.b.c") == 42


def test_get_value_from_path_missing_key_raises():
    """Should raise KeyError if a key in the path is missing."""
    obj = {"a": {"b": 2}}
    with pytest.raises(KeyError, match="Path 'a.x' not found in object"):
        get_value_from_path(obj, "a.x")


def test_get_value_from_path_empty_path_raises():
    """Should raise KeyError if path is empty."""
    obj = {"a": 1}
    with pytest.raises(KeyError, match="Path cannot be empty"):
        get_value_from_path(obj, "")


# endregion

# region: prep_arguments_for_strategy_step_function
def test_prep_arguments_returns_expected_dict():
    """Should return correct mapping for valid context and config."""
    config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={"trend": "trend"},
        context_outputs={},
        config_mapping={"frame_size": "config.extreme.frame_size"}
    )
    context_data = {"trend": "UP"}
    config_data = {"config": {"extreme": {"frame_size": 5}}}
    args = prep_arguments_for_strategy_step_function(config=config, context=context_data, kwargs=config_data)
    assert args == {"trend": "UP", "frame_size": 5}


def test_prep_arguments_missing_context_key_raises_keyerror():
    """Should raise KeyError if a required context key is missing."""
    config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={"trend": "trend", "momentum": "momentum"},
        context_outputs={},
        config_mapping={"frame_size": "config.extreme.frame_size"}
    )
    context_data = {"trend": "UP"}  # 'momentum' is missing
    config_data = {"config": {"extreme": {"frame_size": 5}}}
    with pytest.raises(KeyError, match="Path 'momentum' not found in object"):
        prep_arguments_for_strategy_step_function(config=config, context=context_data, kwargs=config_data)


def test_prep_arguments_missing_config_key_raises_keyerror():
    """Should raise KeyError if a required config key is missing."""
    config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={"trend": "trend"},
        context_outputs={},
        config_mapping={
            "frame_size": "config.extreme.frame_size",
            "threshold": "config.extreme.threshold"  # will be missing in config_data
        }
    )
    context_data = {"trend": "UP"}
    config_data = {"config": {"extreme": {"frame_size": 5}}}  # 'threshold' is missing
    with pytest.raises(KeyError, match="Path 'config.extreme.threshold' not found in object"):
        prep_arguments_for_strategy_step_function(config=config, context=context_data, kwargs=config_data)


def test_prep_arguments_empty_inputs_returns_empty_dict():
    """Should return empty dict if no mappings are provided."""
    config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={},
        config_mapping={}
    )
    context_data = {}
    config_data = {}
    args = prep_arguments_for_strategy_step_function(config=config, context=context_data, kwargs=config_data)
    assert args == {}


def test_prep_arguments_extra_keys_ignored():
    """Should ignore extra keys in context/config not referenced in mappings."""
    config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={"trend": "trend"},
        context_outputs={},
        config_mapping={}
    )
    context_data = {"trend": "UP", "extra": 123}
    config_data = {"unused": True}
    args = prep_arguments_for_strategy_step_function(config=config, context=context_data, kwargs=config_data)
    assert args == {"trend": "UP"}


# endregion

# region: map_strategy_step_function_results
def test_map_strategy_step_function_results_dict_result():
    """Should map output from a nested dict result."""
    config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={"trend": "analysis.direction"},
        config_mapping={}
    )
    result = {"analysis": {"direction": "UP"}}
    mapped = map_strategy_step_function_results(config, result)
    assert mapped == {"trend": "UP"}


def test_map_strategy_step_function_results_non_dict_result():
    """Should map output from a non-dict result (wraps in 'result')."""
    config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={"trend": "result"},
        config_mapping={}
    )
    result = "UP"
    mapped = map_strategy_step_function_results(config, result)
    assert mapped == {"trend": "UP"}


# endregion

# region: Nested Path Handling
def test_evaluate_with_nested_paths():
    """Should extract values from deep nested paths in the result."""
    mock_pure_function = MagicMock(return_value={
        "analysis": {
            "trend": {
                "direction": "DOWN",
                "strength": "weak"
            },
            "confidence": 0.42
        }
    })

    step_config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={
            "trend_direction": "analysis.trend.direction",
            "trend_strength": "analysis.trend.strength",
            "confidence": "analysis.confidence"
        },
        config_mapping={}
    )

    step = StepEvaluator(step_config, mock_pure_function)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {
        "trend_direction": "DOWN",
        "trend_strength": "weak",
        "confidence": 0.42
    }
    assert context.get_latest_strategey_step_output_result("trend_direction") == "DOWN"
    assert context.get_latest_strategey_step_output_result("trend_strength") == "weak"
    assert context.get_latest_strategey_step_output_result("confidence") == 0.42
# endregion


# region: Return Value Handling
def test_evaluate_with_non_dict_result():
    """Should handle non-dict return values by wrapping them."""
    mock_pure_function = MagicMock(return_value=42)

    step_config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={"answer": "result"},
        config_mapping={}
    )

    step = StepEvaluator(step_config, mock_pure_function)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {"answer": 42}
    assert context.get_latest_strategey_step_output_result("answer") == 42
# endregion


# region: Error Handling
def test_evaluate_with_invalid_mapping():
    """Should fail if output mapping path does not exist in result."""
    mock_pure_function = MagicMock(return_value={
        "direction": "UP"
    })

    step_config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={
            "trend": "direction",
            "trend_strength": "strength"  # 'strength' does not exist in result
        },
        config_mapping={}
    )

    step = StepEvaluator(step_config, mock_pure_function)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    assert not result.is_success
    assert "Path 'strength' not found in object" in result.message
    assert context.get_latest_strategey_step_output_result("trend") is None
    assert context.get_latest_strategey_step_output_result("trend_strength") is None 