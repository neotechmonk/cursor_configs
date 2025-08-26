"""Tests for step registry loader."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from loaders.step_registry_loader import create_step_template, load_step_registry


def test_create_step_template_success():
    """Test successfully creating a step template."""
    template_data = {
        "name": "test_step",
        "description": "A test step",
        "parameters": {"param1": "string", "param2": "int"},
        "function_path": "tests.mocks.mock_strategy_step_functions.test_function"
    }
    
    with patch('loaders.step_registry_loader.StrategyStepTemplate') as mock_template_class:
        mock_template = MagicMock()
        mock_template_class.return_value = mock_template
        
        result = create_step_template(template_data)
        
        assert result == mock_template
        mock_template_class.assert_called_once_with(**template_data)


def test_create_step_template_validation_error():
    """Test that validation errors are raised."""
    invalid_template_data = {
        "name": "test_step",
        "invalid_field": "value"  # This should cause validation error
    }
    
    with patch('loaders.step_registry_loader.StrategyStepTemplate') as mock_template_class:
        mock_template_class.side_effect = Exception("Validation error")
        
        with pytest.raises(Exception, match="Validation error"):
            create_step_template(invalid_template_data)


@pytest.fixture
def registry_file(tmp_path):
    """Create a temporary registry file for testing."""
    return tmp_path / "strategy_steps.yaml"


def test_load_step_registry_success(registry_file):
    """Test successfully loading step registry from file."""
    registry_data = {
        "steps": {
            "step1": {
                "name": "Test Step 1",
                "description": "First test step",
                "parameters": {"param1": "string"},
                "function_path": "tests.mocks.mock_strategy_step_functions.step1"
            },
            "step2": {
                "name": "Test Step 2",
                "description": "Second test step",
                "parameters": {"param2": "int"},
                "function_path": "tests.mocks.mock_strategy_step_functions.step2"
            }
        }
    }
    
    with open(registry_file, "w") as f:
        yaml.dump(registry_data, f)
    
    with patch('loaders.step_registry_loader.create_step_template') as mock_create, \
         patch('loaders.step_registry_loader.StrategyStepRegistry') as mock_registry_class:
        
        mock_template1 = MagicMock()
        mock_template2 = MagicMock()
        mock_create.side_effect = [mock_template1, mock_template2]
        
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        result = load_step_registry(registry_file)
        
        assert result == mock_registry
        # Verify create_step_template was called for each step
        assert mock_create.call_count == 2
        
        # Verify the first call included system_step_id
        first_call_args = mock_create.call_args_list[0][0][0]
        assert first_call_args["system_step_id"] == "step1"
        assert first_call_args["name"] == "Test Step 1"
        
        # Verify the second call included system_step_id
        second_call_args = mock_create.call_args_list[1][0][0]
        assert second_call_args["system_step_id"] == "step2"
        assert second_call_args["name"] == "Test Step 2"


def test_load_step_registry_file_not_found():
    """Test loading registry from nonexistent file."""
    nonexistent_file = Path("nonexistent.yaml")
    
    with pytest.raises(FileNotFoundError, match="Registry file not found"):
        load_step_registry(nonexistent_file)


def test_load_step_registry_invalid_yaml(registry_file):
    """Test loading registry with invalid YAML."""
    with open(registry_file, "w") as f:
        f.write("invalid: yaml: content: [")
    
    with pytest.raises(yaml.YAMLError):
        load_step_registry(registry_file)


def test_load_step_registry_missing_steps_key(registry_file):
    """Test loading registry with missing 'steps' key."""
    registry_data = {
        "other_key": "value"
    }
    
    with open(registry_file, "w") as f:
        yaml.dump(registry_data, f)
    
    with pytest.raises(ValueError, match="YAML must contain a 'steps' key with step definitions"):
        load_step_registry(registry_file)


def test_load_step_registry_empty_steps(registry_file):
    """Test loading registry with empty steps."""
    registry_data = {
        "steps": {}
    }
    
    with open(registry_file, "w") as f:
        yaml.dump(registry_data, f)
    
    with patch('loaders.step_registry_loader.StrategyStepRegistry') as mock_registry_class:
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        result = load_step_registry(registry_file)
        
        assert result == mock_registry
        mock_registry_class.assert_called_once_with(steps={})


def test_load_step_registry_validation_error(registry_file):
    """Test that ValidationError is raised for invalid registry config."""
    registry_data = {
        "steps": {
            "step1": {
                "name": "Test Step 1",
                "invalid_field": "value"  # This should cause validation error
            }
        }
    }
    
    with open(registry_file, "w") as f:
        yaml.dump(registry_data, f)
    
    with patch('loaders.step_registry_loader.create_step_template') as mock_create:
        mock_create.side_effect = Exception("Validation error")
        
        with pytest.raises(Exception, match="Validation error"):
            load_step_registry(registry_file)


def test_load_step_registry_system_step_id_injection(registry_file):
    """Test that system_step_id is properly injected into template data."""
    registry_data = {
        "steps": {
            "custom_step_id": {
                "name": "Custom Step",
                "description": "A custom step",
                "parameters": {"param": "string"},
                "function_path": "tests.mocks.mock_strategy_step_functions.custom_step"
            }
        }
    }
    
    with open(registry_file, "w") as f:
        yaml.dump(registry_data, f)
    
    with patch('loaders.step_registry_loader.create_step_template') as mock_create, \
         patch('loaders.step_registry_loader.StrategyStepRegistry') as mock_registry_class:
        
        mock_template = MagicMock()
        mock_create.return_value = mock_template
        
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        load_step_registry(registry_file)
        
        # Verify that system_step_id was injected
        mock_create.assert_called_once_with({
            "name": "Custom Step",
            "description": "A custom step",
            "parameters": {"param": "string"},
            "function_path": "tests.mocks.mock_strategy_step_functions.custom_step",
            "system_step_id": "custom_step_id"
        })


def test_load_step_registry_default_path():
    """Test that default path is used when no path is provided."""
    # This test verifies that the function has a default parameter
    # We don't actually call it since it would fail without a real file
    import inspect
    
    sig = inspect.signature(load_step_registry)
    default_param = sig.parameters['registry_file']
    
    assert default_param.default == Path("configs/strategy_steps.yaml")
