from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.models import StrategyExecutionContext
from src.sandbox.models import StrategyStepTemplate
from src.sandbox.strategy_step_evaluator import StepEvaluator


def test_step_evaluator_success():
    """Should successfully evaluate a step and update context."""
    mock_pure_function = MagicMock(return_value={"trend": "UP"})
    step_config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={"trend": "trend"},
        config_mapping={}
    )
    step = StepEvaluator(step_config, mock_pure_function)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    assert result.is_success
    assert result.message == "Step completed successfully"
    assert result.step_output == {"trend": "UP"}
    assert context.get_latest_strategey_step_output_result("trend") == "UP"


def test_step_evaluator_error():
    """Should handle errors and return failure result."""
    mock_pure_function = MagicMock(side_effect=ValueError("Test error"))
    step_config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={"trend": "trend"},
        config_mapping={}
    )
    step = StepEvaluator(step_config, mock_pure_function)
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    result = step.evaluate(price_feed, context)

    assert not result.is_success
    assert result.message == "Test error"
    assert result.step_output == {}
    assert context.get_latest_strategey_step_output_result("trend") is None


def test_step_evaluator_signature_validation():
    """Should validate function signature on initialization."""
    # Create a function with the expected signature
    def test_function(price_feed, trend, frame_size):
        return {"result": "test"}

    step_config = StrategyStepTemplate(
        pure_function="test_function",
        context_inputs={"trend": "trend"},
        context_outputs={"result": "result"},
        config_mapping={"frame_size": "config.frame_size"}
    )

    # This should work
    evaluator = StepEvaluator(step_config, test_function)
    assert isinstance(evaluator, StepEvaluator)


def test_step_evaluator_invalid_signature():
    """Should raise error if function signature doesn't match config."""
    # Create a function missing the frame_size parameter
    def test_function(price_feed, trend):
        return {"result": "test"}

    step_config = StrategyStepTemplate(
        pure_function="test_function",
        context_inputs={"trend": "trend"},
        context_outputs={"result": "result"},
        config_mapping={"frame_size": "config.frame_size"}
    )

    with pytest.raises(ValueError, match="Pure function missing required parameter from config: frame_size"):
        StepEvaluator(step_config, test_function)


def test_evaluate_success():
    """Should successfully evaluate a step with nested outputs."""
    mock_pure_function = MagicMock(return_value={
        "analysis": {
            "direction": "UP",
            "strength": "strong"
        }
    })

    step_config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={
            "trend": "analysis.direction",
            "trend_strength": "analysis.strength"
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
        "trend": "UP",
        "trend_strength": "strong"
    }
    assert context.get_latest_strategey_step_output_result("trend") == "UP"
    assert context.get_latest_strategey_step_output_result("trend_strength") == "strong"


def test_evaluate_with_empty_context():
    """Should handle empty context inputs gracefully."""
    mock_pure_function = MagicMock(return_value={
        "direction": "UP",
        "strength": "strong"
    })

    step_config = StrategyStepTemplate(
        pure_function="mock",
        context_inputs={},
        context_outputs={
            "trend": "direction",
            "trend_strength": "strength"
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
        "trend": "UP",
        "trend_strength": "strong"
    }
    assert context.get_latest_strategey_step_output_result("trend") == "UP"
    assert context.get_latest_strategey_step_output_result("trend_strength") == "strong"
    mock_pure_function.assert_called_once_with(price_feed)


def test_evaluate_with_missing_required_inputs():
    """Should fail if required context inputs are missing."""
    def pure_fn(price_feed, required_param):
        return {"result": required_param}

    step_config = StrategyStepTemplate(
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
    """Should correctly map config values to function parameters."""
    def pure_fn(price_feed, min_bars, max_bars):
        return {
            "is_valid": min_bars <= len(price_feed) <= max_bars,
            "bar_count": len(price_feed)
        }

    step_config = StrategyStepTemplate(
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
        "is_valid": True,
        "bar_count": 3
    }
    assert context.get_latest_strategey_step_output_result("is_valid") is True
    assert context.get_latest_strategey_step_output_result("bar_count") == 3


def test_evaluate_with_pure_function_error():
    """Should handle exceptions from the pure function correctly."""
    def pure_fn(price_feed):
        raise RuntimeError("Something went wrong!")

    step_config = StrategyStepTemplate(
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