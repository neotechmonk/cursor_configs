import pytest

from src.models.strategy import StrategyStep


def test_strategy_step_basic():
    step = StrategyStep(id="step1", name="Step One", evaluation_fn=lambda p, c, **kw: None)
    assert step.id == "step1"
    assert step.name == "Step One"
    assert callable(step.evaluation_fn) 