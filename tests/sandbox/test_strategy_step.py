from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.models import StrategyExecutionContext
from src.sandbox.strategy_step import StrategyStep


def test_evaluate_success():
    # Mock the pure function to return a dict with a nested structure
    mock_pure_function = MagicMock(return_value={
        "analysis": {
            "direction": "UP",
            "strength": "strong"
        }
    })

    # Create a step config with mappings for both direction and strength
    step_config = {
        "context_inputs": {},
        "context_outputs": {
            "trend": "analysis.direction",     # Maps "UP" to "trend"
            "trend_strength": "analysis.strength"  # Maps "strong" to "trend_strength"
        },
        "config_mapping": {}
    }

    # Create a StrategyStep instance
    step = StrategyStep(step_config, mock_pure_function)

    # Create a price feed and context
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    # Execute the step
    result = step.evaluate(price_feed, context)

    # Verify the result
    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {
        "analysis": {
            "direction": "UP",
            "strength": "strong"
        }
    }

    # Verify both values were stored in the context
    # Get the latest result for each key
    trend = context.get_latest_strategey_step_output_result("trend")
    trend_strength = context.get_latest_strategey_step_output_result("trend_strength")
    assert trend == "UP"
    assert trend_strength == "strong"

def test_evaluate_with_empty_context():
    """Test that StrategyStep handles empty context inputs gracefully."""
    # Mock the pure function to return a simple dict
    mock_pure_function = MagicMock(return_value={
        "direction": "UP",
        "strength": "strong"
    })

    # Create a step config with empty context inputs
    step_config = {
        "context_inputs": {},  # Empty context inputs
        "context_outputs": {
            "trend": "direction",
            "trend_strength": "strength"
        },
        "config_mapping": {}
    }

    # Create a StrategyStep instance
    step = StrategyStep(step_config, mock_pure_function)

    # Create a price feed and empty context
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    # Execute the step
    result = step.evaluate(price_feed, context)

    # Verify the result
    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {
        "direction": "UP",
        "strength": "strong"
    }

    # Verify values were stored in the context
    trend = context.get_latest_strategey_step_output_result("trend")
    trend_strength = context.get_latest_strategey_step_output_result("trend_strength")
    assert trend == "UP"
    assert trend_strength == "strong"

    # Verify the pure function was called with only price_feed
    mock_pure_function.assert_called_once_with(price_feed)

def test_evaluate_with_invalid_mapping():
    """Test that StrategyStep fails when context output mappings are invalid."""
    # Mock the pure function to return a dict without the expected key
    mock_pure_function = MagicMock(return_value={
        "direction": "UP"
    })

    # Create a step config with an invalid mapping (non-existent path)
    step_config = {
        "context_inputs": {},
        "context_outputs": {
            "trend": "direction",
            "trend_strength": "strength"  # 'strength' does not exist in result
        },
        "config_mapping": {}
    }

    step = StrategyStep(step_config, mock_pure_function)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    # Should fail when mapping is invalid
    assert not result.is_success
    assert "Path 'strength' not found in object" in result.message
    # No values should be stored in context
    assert context.get_latest_strategey_step_output_result("trend") is None
    assert context.get_latest_strategey_step_output_result("trend_strength") is None

def test_evaluate_with_nested_paths():
    """Test that StrategyStep can extract values from deep nested paths."""
    mock_pure_function = MagicMock(return_value={
        "analysis": {
            "trend": {
                "direction": "DOWN",
                "strength": "weak"
            },
            "confidence": 0.42
        }
    })

    step_config = {
        "context_inputs": {},
        "context_outputs": {
            "trend_direction": "analysis.trend.direction",
            "trend_strength": "analysis.trend.strength",
            "confidence": "analysis.confidence"
        },
        "config_mapping": {}
    }

    step = StrategyStep(step_config, mock_pure_function)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {
        "analysis": {
            "trend": {
                "direction": "DOWN",
                "strength": "weak"
            },
            "confidence": 0.42
        }
    }
    assert context.get_latest_strategey_step_output_result("trend_direction") == "DOWN"
    assert context.get_latest_strategey_step_output_result("trend_strength") == "weak"
    assert context.get_latest_strategey_step_output_result("confidence") == 0.42

def test_evaluate_with_non_dict_result():
    """Test that StrategyStep handles non-dictionary return values by wrapping them."""
    mock_pure_function = MagicMock(return_value=42)

    step_config = {
        "context_inputs": {},
        "context_outputs": {
            "answer": "result"
        },
        "config_mapping": {}
    }

    step = StrategyStep(step_config, mock_pure_function)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {"result": 42}
    assert context.get_latest_strategey_step_output_result("answer") == 42 