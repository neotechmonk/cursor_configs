from models import Direction, PriceLabel

# Remove StrategyExecutionContext imports, moved to test_strategy_context.py
# from src.models import (
#     StrategStepEvaluationResult,
#     StrategyExecutionContext,
#     StrategyStep,
# )


def test_direction_enum():
    assert Direction.UP.value == "UP"
    assert Direction.DOWN.value == "DOWN"
    assert Direction.RANGE.value == "RANGE"


def test_price_label_enum():
    assert PriceLabel.OPEN.value == "Open"
    assert PriceLabel.HIGH.value == "High"
    assert PriceLabel.LOW.value == "Low"
    assert PriceLabel.CLOSE.value == "Close"


# test_strategy_execution_context_add_result_duplicate_data moved to test_strategy_context.py


# test_strategy_execution_context_add_result_duplicate_data_same_step moved to test_strategy_context.py


# Removed dummy fixture definitions, assumed to be in conftest.py or local to test_strategy_context.py
