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
    assert context.get_latest_strategey_step_output_result("trend") == "UP"
    assert context.get_latest_strategey_step_output_result("trend_strength") == "strong" 