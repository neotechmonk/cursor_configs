"""Tests for StrategyStepRegistry class."""

import sys
from pathlib import Path

import pytest
import yaml

from src.models.system import StrategyStepRegistry

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


def test_load_valid_registry():
    """Test loading a valid registry from YAML."""
    data = yaml.safe_load(VALID_YAML)
    registry = StrategyStepRegistry(**data)
    
    assert "trend_analysis" in registry.step_template_names
    step = registry.get_step_template("trend_analysis")
    assert step.function == "src.utils.get_trend"
    assert step.input_params_map["price_data"] == "market.prices"
    assert step.input_params_map["volume_data"] == "market.volumes"
    assert step.return_map["trend"] == "_"
    assert step.return_map["strength"] == "analysis.strength"
    assert step.config_mapping["window_size"] == "window_size"
    assert step.config_mapping["threshold"] == "threshold"


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
    assert registry.step_templates[0].function == "src.utils.get_trend"


def test_load_from_actual_yaml():
    """Test loading registry from the actual YAML file."""
    registry = StrategyStepRegistry.from_yaml()
    assert isinstance(registry, StrategyStepRegistry)
    assert isinstance(registry.steps, dict)
    assert len(registry.steps) > 0


def test_get_step_template_not_found():
    """Test getting a non-existent step template."""
    data = yaml.safe_load(VALID_YAML)
    registry = StrategyStepRegistry(**data)
    
    with pytest.raises(KeyError, match="Step 'non_existent' not found in registry"):
        registry.get_step_template("non_existent") 