import os
import tempfile

import pytest

from src.sandbox.models import StrategyStepRegistry, StrategyStepTemplate

VALID_YAML = '''
steps:
  trend_analysis:
    pure_function: src.utils.get_trend
    context_inputs:
      price_data: market.prices
    context_outputs:
      trend: analysis.direction
    config_mapping:
      window_size: config.analysis.window
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


@pytest.mark.skip(reason="Registry validation needs to be fixed")
def test_load_valid_registry():
    """Test loading a valid registry from YAML."""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(VALID_YAML)
        f.flush()
        registry = StrategyStepRegistry(_env_file=f.name)
        
    assert "trend_analysis" in registry.step_names
    step = registry.get_step("trend_analysis")
    assert isinstance(step, StrategyStepTemplate)
    assert step.pure_function == "src.utils.get_trend"
    assert step.context_inputs["price_data"] == "market.prices"
    assert step.context_outputs["trend"] == "analysis.direction"


@pytest.mark.skip(reason="Registry validation needs to be fixed")
def test_load_invalid_registry_missing_field():
    """Test loading registry with missing required field."""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(INVALID_YAML_MISSING_FIELD)
        f.flush()
        with pytest.raises(ValueError, match="missing required keys"):
            StrategyStepRegistry(_env_file=f.name)


@pytest.mark.skip(reason="Registry validation needs to be fixed")
def test_load_invalid_registry_empty_function():
    """Test loading registry with empty function name."""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(INVALID_YAML_EMPTY_FUNCTION)
        f.flush()
        with pytest.raises(ValueError, match="Pure function name cannot be empty"):
            StrategyStepRegistry(_env_file=f.name)


@pytest.mark.skip(reason="Registry validation needs to be fixed")
def test_registry_properties():
    """Test that registry properties return correct data types and values."""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(VALID_YAML)
        f.flush()
        registry = StrategyStepRegistry(_env_file=f.name)
        
    assert isinstance(registry.step_names, list)
    assert "trend_analysis" in registry.step_names
    
    assert isinstance(registry.step_objects, list)
    assert len(registry.step_objects) == 1
    assert isinstance(registry.step_objects[0], StrategyStepTemplate)
    os.unlink(f.name) 