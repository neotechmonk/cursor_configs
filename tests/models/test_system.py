import sys
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from src.models.system import StrategyStepRegistry, StrategyStepTemplate

# Add src to Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

# Test data
VALID_YAML = '''
steps:
  trend_analysis:
    function: src.utils.get_trend
    input_params_map:
      price_data: market.prices
      volume_data: market.volumes
    return_map:
      trend: "_"
      strength: analysis.strength
    config_mapping:
      window_size: window_size
      threshold: threshold

config_mapping:
  frame_size: frame_size
  min_bars: min_bars
  max_bars: max_bars
  min_fib_extension: min_fib_extension
  max_fib_extension: max_fib_extension
'''

INVALID_YAML_MISSING_FIELD = '''
steps:
  trend_analysis:
    input_params_map:
      price_data: market.prices
    return_map:
      trend: "_"
'''

INVALID_YAML_EMPTY_FUNCTION = '''
steps:
  trend_analysis:
    function: ""
    input_params_map:
      price_data: market.prices
    return_map:
      trend: "_"
'''

# StrategyStepTemplate Tests
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

# StrategyStepRegistry Tests
def test_load_valid_registry():
    """Test loading a valid registry from YAML."""
    data = yaml.safe_load(VALID_YAML)
    registry = StrategyStepRegistry(**data)
    
    assert "trend_analysis" in registry.step_template_names
    step = registry.get_step_template("trend_analysis")
    assert isinstance(step, StrategyStepTemplate)
    assert step.function == "src.utils.get_trend"
    assert step.input_params_map["price_data"] == "market.prices"
    assert step.input_params_map["volume_data"] == "market.volumes"
    assert step.return_map["trend"] == "_"
    assert step.return_map["strength"] == "analysis.strength"
    assert step.config_mapping["window_size"] == "window_size"
    assert step.config_mapping["threshold"] == "threshold"
    
    # Test global config mapping
    assert registry.config_mapping["frame_size"] == "frame_size"
    assert registry.config_mapping["min_bars"] == "min_bars"
    assert registry.config_mapping["max_bars"] == "max_bars"
    assert registry.config_mapping["min_fib_extension"] == "min_fib_extension"
    assert registry.config_mapping["max_fib_extension"] == "max_fib_extension"


def test_load_invalid_registry_missing_field():
    """Test loading registry with missing required field."""
    data = yaml.safe_load(INVALID_YAML_MISSING_FIELD)
    with pytest.raises(ValueError, match="function"):
        StrategyStepRegistry(**data)


def test_load_invalid_registry_empty_function():
    """Test loading registry with empty function name."""
    data = yaml.safe_load(INVALID_YAML_EMPTY_FUNCTION)
    with pytest.raises(ValueError, match="Function name cannot be empty"):
        StrategyStepRegistry(**data)


def test_registry_properties():
    """Test that registry properties return correct data types and values."""
    data = yaml.safe_load(VALID_YAML)
    registry = StrategyStepRegistry(**data)
    
    assert isinstance(registry.step_template_names, list)
    assert "trend_analysis" in registry.step_template_names
    
    assert isinstance(registry.step_templates, list)
    assert len(registry.step_templates) == 1
    assert isinstance(registry.step_templates[0], StrategyStepTemplate)
    
    assert isinstance(registry.config_mapping, dict)
    assert "frame_size" in registry.config_mapping

def test_load_from_actual_yaml():
    """Test loading registry from the actual YAML file."""
    registry = StrategyStepRegistry.from_yaml()
    assert isinstance(registry, StrategyStepRegistry)
    assert isinstance(registry.config_mapping, dict)
    assert "frame_size" in registry.config_mapping
    assert "min_bars" in registry.config_mapping
    assert "max_bars" in registry.config_mapping
    assert "min_fib_extension" in registry.config_mapping
    assert "max_fib_extension" in registry.config_mapping 