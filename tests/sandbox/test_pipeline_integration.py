import pandas as pd

from src.models import StrategyExecutionContext
from src.sandbox.models import StrategyStepTemplate
from src.sandbox.strategy_step_evaluator import StepEvaluator


def test_pipeline_step_integration():
    # Create a step template directly
    step_config = StrategyStepTemplate(
        pure_function="mock_get_trend",
        context_inputs={},
        context_outputs={"trend": "direction"},
        config_mapping={}
    )

    # Mock the function (simulate src.utils.mock_get_trend)
    def mock_get_trend(price_feed):
        return {"direction": "UP"}

    # Create evaluator
    evaluator = StepEvaluator(step_config, mock_get_trend)

    # Prepare data and context
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    # Run the step
    result = evaluator.evaluate(price_feed, context)

    assert result.is_success
    assert result.step_output == {"trend": "UP"}
    assert context.get_latest_strategey_step_output_result("trend") == "UP" 