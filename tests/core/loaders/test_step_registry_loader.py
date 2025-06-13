"""Tests for the step registry loader."""

import pytest
import yaml
from pydantic import ValidationError

from src.loaders.step_registry_loader import create_step_template, load_step_registry
from src.models.system import StrategyStepTemplate


@pytest.fixture
def mock_registry_file(tmp_path):
    """Create a mock registry file."""
    registry_file = tmp_path / "registry.yaml"
    registry = {
        "steps": {
            "detect_trend": {
                "system_step_id": "detect_trend",
                "function": "test.get_trend",
                "input_params_map": {
                    "valid_input": "source"
                },
                "return_map": {
                    "trend": "_"
                },
                "config_mapping": {
                    "valid_param": "source"
                }
            }
        }
    }
    with open(registry_file, "w") as f:
        yaml.safe_dump(registry, f)
    return registry_file


def test_create_step_template_valid():
    """Test creating a valid step template."""
    template_data = {
        "system_step_id": "detect_trend",
        "function": "test.get_trend",
        "input_params_map": {
            "valid_input": "source"
        },
        "return_map": {
            "trend": "_"
        },
        "config_mapping": {
            "valid_param": "source"
        }
    }
    
    template = create_step_template(template_data)
    
    assert isinstance(template, StrategyStepTemplate)
    assert template.system_step_id == "detect_trend"
    assert template.function == "test.get_trend"
    assert template.input_params_map == {"valid_input": "source"}
    assert template.return_map == {"trend": "_"}
    assert template.config_mapping == {"valid_param": "source"}


def test_create_step_template_invalid():
    """Test creating an invalid step template."""
    template_data = {
        "system_step_id": "detect_trend",
        # Missing required fields
    }
    
    with pytest.raises(ValidationError):
        create_step_template(template_data)


def test_load_step_registry(mock_registry_file):
    """Test loading a step registry from file."""
    registry = load_step_registry(mock_registry_file)
    
    assert "detect_trend" in registry.step_template_names
    template = registry.get_step_template("detect_trend")
    assert template.system_step_id == "detect_trend"
    assert template.function == "test.get_trend"
    assert template.input_params_map == {"valid_input": "source"}
    assert template.return_map == {"trend": "_"}
    assert template.config_mapping == {"valid_param": "source"}


def test_load_step_registry_missing_file(tmp_path):
    """Test loading registry with missing file."""
    registry_file = tmp_path / "nonexistent.yaml"
    
    with pytest.raises(FileNotFoundError):
        load_step_registry(registry_file)


def test_load_step_registry_invalid_yaml(tmp_path):
    """Test loading registry with invalid YAML."""
    registry_file = tmp_path / "invalid.yaml"
    registry_file.write_text("invalid: yaml: content:")
    
    with pytest.raises(Exception):  # Could be yaml.YAMLError or ValidationError
        load_step_registry(registry_file)


def test_load_step_registry_invalid_config(tmp_path):
    """Test loading registry with invalid template config."""
    registry_file = tmp_path / "invalid_config.yaml"
    registry = {
        "steps": {
            "detect_trend": {
                "system_step_id": "detect_trend",
                # Missing required fields
            }
        }
    }
    with open(registry_file, "w") as f:
        yaml.safe_dump(registry, f)
    
    with pytest.raises(ValidationError):
        load_step_registry(registry_file) 