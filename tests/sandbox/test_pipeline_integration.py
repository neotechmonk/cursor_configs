import pandas as pd

from src.models import StrategyExecutionContext
from src.sandbox.pipeline_config import PipelineConfig
from src.sandbox.pipeline_runtime import StrategyStepFactory


def test_pipeline_step_integration(tmp_path):
    # Write a minimal valid config to a temp file
    config_yaml = """
steps:
  detect_trend:
    pure_function: "src.utils.mock_get_trend"
    context_inputs: {}
    context_outputs:
      trend: "direction"
    config_mapping: {}
"""
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(config_yaml)

    # Load config
    pipeline_config = PipelineConfig(str(config_path))
    factory = StrategyStepFactory(pipeline_config)

    # Mock the function (simulate src.utils.mock_get_trend)
    def mock_get_trend(price_feed):
        return {"direction": "UP"}

    # Create evaluator
    evaluator = factory.create_evaluator("detect_trend", mock_get_trend)

    # Prepare data and context
    price_feed = pd.DataFrame({"Open": [100, 101, 102]})
    context = StrategyExecutionContext()

    # Run the step
    result = evaluator.evaluate(price_feed, context)

    assert result.is_success
    assert result.step_output == {"trend": "UP"}
    assert context.get_latest_strategey_step_output_result("trend") == "UP" 