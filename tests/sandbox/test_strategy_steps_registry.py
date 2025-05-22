import os
import tempfile

import pytest
import yaml
from pydantic import ConfigDict

from src.sandbox.models import StrategyStepRegistry, StrategyStepTemplate

VALID_YAML = '''
steps:
  trend_analysis:
    pure_function: src.utils.get_trend
    context_inputs:
      price_data: market.prices
      volume_data: market.volumes
    context_outputs:
      trend: analysis.direction
      strength: analysis.strength
    config_mapping:
      window_size: config.analysis.window
      threshold: config.analysis.threshold
'''

INVALID_YAML_MISSING_FIELD = '''
steps:
  trend_analysis:
    context_inputs:
      price_data: market.prices
    context_outputs:
      trend: analysis.direction
'''

INVALID_YAML_EMPTY_FUNCTION = '''
steps:
  trend_analysis:
    pure_function: ""
    context_inputs:
      price_data: market.prices
    context_outputs:
      trend: analysis.direction
'''


def test_load_valid_registry():
    """Test loading a valid registry from YAML."""
    data = yaml.safe_load(VALID_YAML)
    registry = StrategyStepRegistry(**data)
    
    assert "trend_analysis" in registry.step_template_names
    step = registry.get_step_template("trend_analysis")
    assert isinstance(step, StrategyStepTemplate)
    assert step.pure_function == "src.utils.get_trend"
    assert step.context_inputs["price_data"] == "market.prices"
    assert step.context_inputs["volume_data"] == "market.volumes"
    assert step.context_outputs["trend"] == "analysis.direction"
    assert step.context_outputs["strength"] == "analysis.strength"
    assert step.config_mapping["window_size"] == "config.analysis.window"
    assert step.config_mapping["threshold"] == "config.analysis.threshold"


def test_load_invalid_registry_missing_field():
    """Test loading registry with missing required field."""
    data = yaml.safe_load(INVALID_YAML_MISSING_FIELD)
    with pytest.raises(ValueError, match="pure_function"):
        StrategyStepRegistry(**data)


def test_load_invalid_registry_empty_function():
    """Test loading registry with empty function name."""
    data = yaml.safe_load(INVALID_YAML_EMPTY_FUNCTION)
    with pytest.raises(ValueError, match="Pure function name cannot be empty"):
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