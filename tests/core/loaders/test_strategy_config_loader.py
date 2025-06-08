"""Tests for the strategy configuration loader."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from src.loaders.strategy_config_loader import load_strategy_configs
from src.models.system import StrategyStepRegistry, StrategyStepTemplate


@pytest.fixture
def mock_strategy_dir(tmp_path):
    """Create a temporary directory with mock strategy configs."""
    strategy_dir = tmp_path / "strategies"
    strategy_dir.mkdir()
    
    # Create a valid strategy config
    valid_strategy = strategy_dir / "valid_strategy.yaml"
    valid_strategy.write_text("""
name: "Test Strategy"
steps:
  - system_step_id: detect_trend
    description: "Test step"
    static_config: {}
    dynamic_config: {}
    """)
    
    return strategy_dir


@pytest.fixture
def mock_step_registry():
    """Create a mock step registry with validation rules."""
    registry = StrategyStepRegistry(steps={
        "detect_trend": StrategyStepTemplate(
            system_step_id="detect_trend",
            function="test.get_trend",
            input_params_map={
                "valid_input": "source"  # Only this input is allowed
            },
            return_map={"trend": "_"},
            config_mapping={
                "valid_param": "source"  # Only this config is allowed
            }
        )
    })
    return registry


def test_load_valid_strategy(mock_strategy_dir, mock_step_registry):
    """Test loading a valid strategy configuration."""
    strategies = load_strategy_configs(mock_strategy_dir, mock_step_registry)
    
    assert len(strategies) == 1
    assert "Test Strategy" in strategies
    
    strategy = strategies["Test Strategy"]
    assert len(strategy.steps) == 1
    assert strategy.steps[0].system_step_id == "detect_trend"
    assert strategy.steps[0].template is not None

# @pytest.mark.xfail(reason="This test is not debuuged yet")
def test_validate_step_against_template(mock_strategy_dir, mock_step_registry):
    """Test that step configuration is validated against its template."""
    # Add a strategy with invalid config
    invalid_config = mock_strategy_dir / "invalid_config.yaml"
    invalid_config.write_text("""
name: "Invalid Config Strategy"
steps:
  - system_step_id: detect_trend
    description: "Test step"
    static_config:
      invalid_param: "value"  # Not in template's config_mapping
    dynamic_config:
      invalid_input: "value"  # Not in template's input_params_map
    """)
    
    with pytest.raises(ValidationError) as exc_info:
        load_strategy_configs(mock_strategy_dir, mock_step_registry)
    
    error_msg = str(exc_info.value)
    assert "Static config parameter 'invalid_param' not found in template config_mapping" in error_msg
    assert "Dynamic config parameter 'invalid_input' not found in template input_params_map" in error_msg 