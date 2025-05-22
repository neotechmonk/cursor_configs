import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from sandbox.models import StrategyStepTemplate

# Add src to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)


def test_strategy_step_template_instantiation():
    """Test basic instantiation of StrategyStepTemplate with valid data."""
    step = StrategyStepTemplate(
        pure_function="src.utils.get_trend",
        context_inputs={},
        context_outputs={"trend": "analysis.direction"},
        config_mapping={}
    )
    assert step.pure_function == "src.utils.get_trend"
    assert step.context_outputs["trend"] == "analysis.direction"
    assert step.context_inputs == {}
    assert step.config_mapping == {}


def test_strategy_step_template_with_complex_mappings():
    """Test StrategyStepTemplate with complex input/output mappings."""
    step = StrategyStepTemplate(
        pure_function="src.utils.analyze_market",
        context_inputs={
            "price_data": "market.prices",
            "volume_data": "market.volumes"
        },
        context_outputs={
            "trend": "analysis.direction",
            "strength": "analysis.strength",
            "confidence": "analysis.confidence"
        },
        config_mapping={
            "window_size": "config.analysis.window",
            "threshold": "config.analysis.threshold"
        }
    )
    
    assert step.pure_function == "src.utils.analyze_market"
    assert step.context_inputs["price_data"] == "market.prices"
    assert step.context_outputs["trend"] == "analysis.direction"
    assert step.config_mapping["window_size"] == "config.analysis.window"


def test_strategy_step_template_empty_function():
    """Test that empty pure_function raises ValueError."""
    with pytest.raises(ValueError, match="Pure function name cannot be empty"):
        StrategyStepTemplate(
            pure_function="",
            context_inputs={},
            context_outputs={},
            config_mapping={}
        )


def test_strategy_step_template_whitespace_function():
    """Test that whitespace-only pure_function raises ValueError."""
    with pytest.raises(ValueError, match="Pure function name cannot be empty"):
        StrategyStepTemplate(
            pure_function="   ",
            context_inputs={},
            context_outputs={},
            config_mapping={}
        )


def test_strategy_step_template_default_values():
    """Test that optional fields default to empty dicts."""
    step = StrategyStepTemplate(
        pure_function="src.utils.get_trend"
    )
    assert step.context_inputs == {}
    assert step.context_outputs == {}
    assert step.config_mapping == {}


def test_strategy_step_template_immutability():
    """Test that StrategyStepTemplate instances are immutable."""
    step = StrategyStepTemplate(
        pure_function="src.utils.get_trend",
        context_inputs={"input": "value"},
        context_outputs={"output": "value"},
        config_mapping={"config": "value"}
    )
    
    # Attempt to modify fields
    with pytest.raises(ValidationError):
        step.pure_function = "new_function"
    
    # Test dictionary immutability by attempting to modify the model
    with pytest.raises(ValidationError):
        step.context_inputs = {"new_input": "new_value"}
    
    with pytest.raises(ValidationError):
        step.context_outputs = {"new_output": "new_value"}
    
    with pytest.raises(ValidationError):
        step.config_mapping = {"new_config": "new_value"} 