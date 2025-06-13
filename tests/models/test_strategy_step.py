"""Tests for StrategyStep class."""

from models.strategy import StrategyStep
from src.models.system import StrategyStepTemplate


def test_strategy_step_basic():
    """Test basic StrategyStep creation and properties."""
    template = StrategyStepTemplate(
        system_step_id="step1",
        function="src.utils.get_trend",
        input_params_map={"price_data": "market.prices"},
        return_map={"trend": "_"}
    )
    
    step = StrategyStep(
        system_step_id="step1",
        template=template,
        reevaluates=[]
    )
    
    assert step.system_step_id == "step1"
    assert step.template == template
    assert step.reevaluates == [] 