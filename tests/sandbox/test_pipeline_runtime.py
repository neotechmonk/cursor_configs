from unittest.mock import MagicMock

import pandas as pd

from src.models import StrategyExecutionContext
from src.sandbox.pipeline_config import StepConfig
from src.sandbox.pipeline_runtime import StepEvaluator


def test_evaluate_success():
    # Mock the pure function to return a dict with a nested structure
    mock_pure_function = MagicMock(return_value={
        "analysis": {
            "direction": "UP",
            "strength": "strong"
        }
    })

    # Create a step config with mappings for both direction and strength
    step_config = StepConfig(
        pure_function="mock",
        context_inputs={},
        context_outputs={
            "trend": "analysis.direction",     # Maps "UP" to "trend"
            "trend_strength": "analysis.strength"  # Maps "strong" to "trend_strength"
        },
        config_mapping={}
    )

    # Create a StrategyStep instance
    step = StepEvaluator(step_config, mock_pure_function)

    # Create a price feed and context
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    # Execute the step
    result = step.evaluate(price_feed, context)

    # Verify the result
    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {
        "trend": "UP",
        "trend_strength": "strong"
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
    step_config = StepConfig(
        pure_function="mock",
        context_inputs={},  # Empty context inputs
        context_outputs={
            "trend": "direction",
            "trend_strength": "strength"
        },
        config_mapping={}
    )

    # Create a StrategyStep instance
    step = StepEvaluator(step_config, mock_pure_function)

    # Create a price feed and empty context
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    # Execute the step
    result = step.evaluate(price_feed, context)

    # Verify the result
    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {
        "trend": "UP",
        "trend_strength": "strong"
    }

    # Verify values were stored in the context
    trend = context.get_latest_strategey_step_output_result("trend")
    trend_strength = context.get_latest_strategey_step_output_result("trend_strength")
    assert trend == "UP"
    assert trend_strength == "strong"

    # Verify the pure function was called with only price_feed
    mock_pure_function.assert_called_once_with(price_feed)


def test_evaluate_with_missing_required_inputs():
    """Test that StrategyStep fails if required context inputs are missing."""
    # Pure function expects a required argument
    def pure_fn(price_feed, required_param):
        return {"result": required_param}

    step_config = StepConfig(
        pure_function="mock",
        context_inputs={},
        context_outputs={"result": "result"},
        config_mapping={}
    )

    step = StepEvaluator(step_config, pure_fn)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    assert not result.is_success
    assert "required_param" in result.message
    assert context.get_latest_strategey_step_output_result("result") is None


def test_evaluate_with_config_mapping():
    """Test that StrategyStep correctly maps config values to function parameters."""
    # Pure function that uses config values
    def pure_fn(price_feed, min_bars, max_bars):
        return {
            "is_valid": min_bars <= len(price_feed) <= max_bars,
            "bar_count": len(price_feed)
        }

    step_config = StepConfig(
        pure_function="mock",
        context_inputs={},
        context_outputs={
            "is_valid": "is_valid",
            "bar_count": "bar_count"
        },
        config_mapping={
            "min_bars": "config.validation.min_bars",
            "max_bars": "config.validation.max_bars"
        }
    )

    step = StepEvaluator(step_config, pure_fn)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    # Pass config values as keyword arguments
    config = {
        "validation": {
            "min_bars": 2,
            "max_bars": 5
        }
    }

    result = step.evaluate(price_feed, context, config=config)

    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {
        "is_valid": True,  # 3 bars is between min_bars (2) and max_bars (5)
        "bar_count": 3
    }
    assert context.get_latest_strategey_step_output_result("is_valid") is True
    assert context.get_latest_strategey_step_output_result("bar_count") == 3


def test_evaluate_with_pure_function_error():
    """Test that StrategyStep handles exceptions from the pure function correctly."""
    # Pure function that raises an exception
    def pure_fn(price_feed):
        raise RuntimeError("Something went wrong!")

    step_config = StepConfig(
        pure_function="mock",
        context_inputs={},
        context_outputs={"result": "result"},
        config_mapping={}
    )

    step = StepEvaluator(step_config, pure_fn)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    assert not result.is_success
    assert "Something went wrong!" in result.message
    assert result.step_output == {}
    assert context.get_latest_strategey_step_output_result("result") is None 