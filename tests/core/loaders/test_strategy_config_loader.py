"""Tests for the strategy configuration loader."""


import pytest
from pydantic import ValidationError

from src.loaders.strategy_config_loader import create_new_strategy, load_strategies
from src.models.system import StrategyStepRegistry, StrategyStepTemplate


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
        ),
        "find_extreme": StrategyStepTemplate(
            system_step_id="find_extreme",
            function="test.find_extreme",
            input_params_map={},
            return_map={"extreme": "_"},
            config_mapping={}
        )
    })
    return registry


def test_create_new_strategy_valid(mock_step_registry):
    """Test creating a valid strategy configuration."""
    data = {
        "name": "Test Strategy",
        "steps": [
            {
                "system_step_id": "detect_trend",
                "description": "Test step",
                "static_config": {
                    "valid_param": "value"
                },
                "dynamic_config": {
                    "valid_input": "step1.output"
                }
            }
        ]
    }
    
    strategy = create_new_strategy(data, mock_step_registry)
    
    assert strategy.name == "Test Strategy"
    assert len(strategy.steps) == 1
    step = strategy.steps[0]
    assert step.system_step_id == "detect_trend"
    assert step.template is not None
    assert step.static_config == {"valid_param": "value"}
    assert step.dynamic_config == {"valid_input": "step1.output"}


def test_create_new_strategy_invalid_config(mock_step_registry):
    """Test that invalid step configurations are caught."""
    data = {
        "name": "Invalid Strategy",
        "steps": [
            {
                "system_step_id": "detect_trend",
                "description": "Test step",
                "static_config": {
                    "invalid_param": "value"  # Not in template's config_mapping
                },
                "dynamic_config": {
                    "invalid_input": "value"  # Not in template's input_params_map
                }
            }
        ]
    }
    
    with pytest.raises(ValidationError) as exc_info:
        create_new_strategy(data, mock_step_registry)
    
    error_msg = str(exc_info.value)
    assert "Static config parameter 'invalid_param' not found in template config_mapping" in error_msg
    assert "Dynamic config parameter 'invalid_input' not found in template input_params_map" in error_msg


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
    static_config:
      valid_param: "value"
    dynamic_config:
      valid_input: "step1.output"
    """)
    
    return strategy_dir


def test_load_strategies(mock_strategy_dir, mock_step_registry):
    """Test loading strategy configurations from files."""
    strategies = load_strategies(mock_strategy_dir, mock_step_registry)
    
    assert len(strategies) == 1
    assert "Test Strategy" in strategies
    
    strategy = strategies["Test Strategy"]
    assert len(strategy.steps) == 1
    step = strategy.steps[0]
    assert step.system_step_id == "detect_trend"
    assert step.template is not None
    assert step.static_config == {"valid_param": "value"}
    assert step.dynamic_config == {"valid_input": "step1.output"}


def test_create_new_strategy_multiple_steps(mock_step_registry):
    """Test creating a strategy with multiple steps using different templates."""
    # Add another template to registry
    mock_step_registry.steps["calculate_signal"] = StrategyStepTemplate(
        system_step_id="calculate_signal",
        function="test.calculate",
        input_params_map={"signal_input": "source"},
        return_map={"signal": "_"},
        config_mapping={"signal_param": "source"}
    )
    
    data = {
        "name": "Multi-Step Strategy",
        "steps": [
            {
                "system_step_id": "detect_trend",
                "description": "Trend detection",
                "static_config": {"valid_param": "value"},
                "dynamic_config": {"valid_input": "step1.output"}
            },
            {
                "system_step_id": "calculate_signal",
                "description": "Signal calculation",
                "static_config": {"signal_param": "value"},
                "dynamic_config": {"signal_input": "step1.trend"}
            }
        ]
    }
    
    strategy = create_new_strategy(data, mock_step_registry)
    assert len(strategy.steps) == 2
    assert strategy.steps[0].system_step_id == "detect_trend"
    assert strategy.steps[1].system_step_id == "calculate_signal"


def test_create_new_strategy_empty_configs(mock_step_registry):
    """Test creating a strategy with empty configs."""
    data = {
        "name": "Empty Config Strategy",
        "steps": [
            {
                "system_step_id": "detect_trend",
                "description": "Test step",
                "static_config": {},
                "dynamic_config": {}
            }
        ]
    }
    
    strategy = create_new_strategy(data, mock_step_registry)
    assert strategy.steps[0].static_config == {}
    assert strategy.steps[0].dynamic_config == {}


def test_create_new_strategy_valid_static_config(mock_step_registry):
    """Test creating a strategy with only valid static config."""
    data = {
        "name": "Valid Static Config Strategy",
        "steps": [
            {
                "system_step_id": "detect_trend",
                "description": "Test step",
                "static_config": {"valid_param": "value"},
                "dynamic_config": {}
            }
        ]
    }
    
    strategy = create_new_strategy(data, mock_step_registry)
    assert strategy.steps[0].static_config == {"valid_param": "value"}
    assert strategy.steps[0].dynamic_config == {}


def test_create_new_strategy_valid_dynamic_config(mock_step_registry):
    """Test creating a strategy with only valid dynamic config."""
    data = {
        "name": "Valid Dynamic Config Strategy",
        "steps": [
            {
                "system_step_id": "detect_trend",
                "description": "Test step",
                "static_config": {},
                "dynamic_config": {"valid_input": "step1.output"}
            }
        ]
    }
    
    strategy = create_new_strategy(data, mock_step_registry)
    assert strategy.steps[0].static_config == {}
    assert strategy.steps[0].dynamic_config == {"valid_input": "step1.output"}


def test_create_new_strategy_mixed_configs(mock_step_registry):
    """Test creating a strategy with mixed valid/invalid configs."""
    data = {
        "name": "Mixed Config Strategy",
        "steps": [
            {
                "system_step_id": "detect_trend",
                "description": "Test step",
                "static_config": {
                    "valid_param": "value",
                    "invalid_param": "value"
                },
                "dynamic_config": {
                    "valid_input": "step1.output",
                    "invalid_input": "value"
                }
            }
        ]
    }
    
    with pytest.raises(ValidationError) as exc_info:
        create_new_strategy(data, mock_step_registry)
    
    error_msg = str(exc_info.value)
    assert "Static config parameter 'invalid_param' not found in template config_mapping" in error_msg
    assert "Dynamic config parameter 'invalid_input' not found in template input_params_map" in error_msg


def test_create_new_strategy_with_reevaluates(mock_step_registry):
    """Test creating a strategy with step dependencies/reevaluations."""
    data = {
        "name": "Strategy With Dependencies",
        "steps": [
            {
                "system_step_id": "detect_trend",
                "description": "First step",
                "static_config": {},
                "dynamic_config": {},
                "reevaluates": []
            },
            {
                "system_step_id": "find_extreme",
                "description": "Second step",
                "static_config": {},
                "dynamic_config": {},
                "reevaluates": ["detect_trend"]  # Depends on first step
            }
        ]
    }
    
    strategy = create_new_strategy(data, mock_step_registry)
    
    assert len(strategy.steps) == 2
    first_step = strategy.steps[0]
    second_step = strategy.steps[1]
    
    # Check that second step has first step in its reevaluates list
    assert len(second_step.reevaluates) == 1
    assert second_step.reevaluates[0].system_step_id == first_step.system_step_id
    assert second_step.reevaluates[0] is first_step  # Should be the same object reference 