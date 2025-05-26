"""Tests for StrategyStepTemplate class."""

import pytest
from pydantic import ValidationError

from src.models.system import StrategyStepTemplate


def test_strategy_step_template_instantiation():
    """Test basic instantiation of StrategyStepTemplate with valid data."""
    step = StrategyStepTemplate(
        function="src.utils.get_trend",
        input_params_map={},
        return_map={"trend": "_"},
        config_mapping={}
    )
    assert step.function == "src.utils.get_trend"
    assert step.return_map["trend"] == "_"
    assert step.input_params_map == {}
    assert step.config_mapping == {}


def test_strategy_step_template_with_complex_mappings():
    """Test StrategyStepTemplate with complex input/output mappings."""
    step = StrategyStepTemplate(
        function="src.utils.analyze_market",
        input_params_map={
            "price_data": "market.prices",
            "volume_data": "market.volumes"
        },
        return_map={
            "trend": "_",
            "strength": "analysis.strength",
            "confidence": "analysis.confidence"
        },
        config_mapping={
            "window_size": "window_size",
            "threshold": "threshold"
        }
    )
    
    assert step.function == "src.utils.analyze_market"
    assert step.input_params_map["price_data"] == "market.prices"
    assert step.return_map["trend"] == "_"
    assert step.config_mapping["window_size"] == "window_size"


def test_strategy_step_template_empty_function():
    """Test that empty function raises ValueError."""
    with pytest.raises(ValueError, match="Function name cannot be empty"):
        StrategyStepTemplate(
            function="",
            input_params_map={},
            return_map={},
            config_mapping={}
        )


def test_strategy_step_template_whitespace_function():
    """Test that whitespace-only function raises ValueError."""
    with pytest.raises(ValueError, match="Function name cannot be empty"):
        StrategyStepTemplate(
            function="   ",
            input_params_map={},
            return_map={},
            config_mapping={}
        )


def test_strategy_step_template_default_values():
    """Test that optional fields default to empty dicts."""
    step = StrategyStepTemplate(
        function="src.utils.get_trend"
    )
    assert step.input_params_map == {}
    assert step.return_map == {}
    assert step.config_mapping == {}


def test_strategy_step_template_immutability():
    """Test that StrategyStepTemplate instances are immutable."""
    step = StrategyStepTemplate(
        function="src.utils.get_trend",
        input_params_map={"input": "value"},
        return_map={"output": "_"},
        config_mapping={"config": "value"}
    )
    
    # Attempt to modify fields
    with pytest.raises(ValidationError):
        step.function = "new_function"
    
    # Test dictionary immutability by attempting to modify the model
    with pytest.raises(ValidationError):
        step.input_params_map = {"new_input": "new_value"}
    
    with pytest.raises(ValidationError):
        step.return_map = {"new_output": "_"}
    
    with pytest.raises(ValidationError):
        step.config_mapping = {"new_config": "new_value"} 