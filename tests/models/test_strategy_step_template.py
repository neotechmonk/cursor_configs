"""Tests for StrategyStepTemplate class."""

import pytest
from pydantic import ValidationError

from src.models.system import StrategyStepTemplate


def test_strategy_step_template_instantiation():
    """Test basic StrategyStepTemplate instantiation."""
    step = StrategyStepTemplate(
        system_step_id="trend_analysis",
        function="src.utils.get_trend",
        input_params_map={"price_data": "market.prices"},
        return_map={"trend": "_"}
    )
    
    assert step.system_step_id == "trend_analysis"
    assert step.function == "src.utils.get_trend"
    assert step.input_params_map == {"price_data": "market.prices"}
    assert step.return_map == {"trend": "_"}
    assert step.config_mapping == {}


def test_strategy_step_template_with_complex_mappings():
    """Test StrategyStepTemplate with complex input/output mappings."""
    step = StrategyStepTemplate(
        system_step_id="trend_analysis",
        function="src.utils.analyze_trend",
        input_params_map={
            "price_data": "market.prices",
            "volume_data": "market.volumes",
            "indicators": "analysis.indicators"
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
    
    assert step.system_step_id == "trend_analysis"
    assert step.function == "src.utils.analyze_trend"
    assert len(step.input_params_map) == 3
    assert len(step.return_map) == 3
    assert len(step.config_mapping) == 2


def test_strategy_step_template_empty_function():
    """Test that empty function raises ValueError."""
    with pytest.raises(ValueError, match="Function name cannot be empty"):
        StrategyStepTemplate(
            system_step_id="trend_analysis",
            function="",
            input_params_map={},
            return_map={},
            config_mapping={}
        )


def test_strategy_step_template_whitespace_function():
    """Test that whitespace-only function raises ValueError."""
    with pytest.raises(ValueError, match="Function name cannot be empty"):
        StrategyStepTemplate(
            system_step_id="trend_analysis",
            function="   ",
            input_params_map={},
            return_map={},
            config_mapping={}
        )


def test_strategy_step_template_default_values():
    """Test StrategyStepTemplate with minimal required fields."""
    step = StrategyStepTemplate(
        system_step_id="trend_analysis",
        function="src.utils.get_trend"
    )
    
    assert step.system_step_id == "trend_analysis"
    assert step.function == "src.utils.get_trend"
    assert step.input_params_map == {}
    assert step.return_map == {}
    assert step.config_mapping == {}


def test_strategy_step_template_immutability():
    """Test that StrategyStepTemplate is immutable.
    
    Note: In Pydantic v2, the model instance itself is frozen (preventing attribute reassignment),
    but the dictionary attributes (input_params_map, return_map, config_mapping) are not frozen.
    This means you can't replace the entire dictionary, but you can modify its contents.
    This test verifies the model-level immutability by attempting to replace attributes.
    """
    step = StrategyStepTemplate(
        system_step_id="trend_analysis",
        function="src.utils.get_trend",
        input_params_map={"price_data": "market.prices"},
        return_map={"trend": "_"},
        config_mapping={"config": "value"}
    )
    
    # Test model-level immutability
    with pytest.raises(ValidationError, match="Instance is frozen"):
        step.function = "new_function"
    
    # Test that we can't replace the entire dictionary
    with pytest.raises(ValidationError, match="Instance is frozen"):
        step.input_params_map = {"new_param": "new_value"}
    
    with pytest.raises(ValidationError, match="Instance is frozen"):
        step.return_map = {"new_output": "new_value"}
    
    with pytest.raises(ValidationError, match="Instance is frozen"):
        step.config_mapping = {"new_config": "new_value"} 