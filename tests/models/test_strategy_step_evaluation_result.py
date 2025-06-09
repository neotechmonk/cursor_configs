
from src.models.strategy import StrategyStepEvaluationResult


def test_strategy_step_evaluation_result_basic():
    result = StrategyStepEvaluationResult(is_success=True, message="OK", step_output={"foo": "bar"})
    assert result.is_success is True
    assert result.message == "OK"
    assert result.step_output == {"foo": "bar"} 