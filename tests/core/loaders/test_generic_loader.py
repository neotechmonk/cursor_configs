# tests/core/loaders/test_generic_loader.py

"""Tests for the generic YAML configuration loader."""


import pytest
import yaml
from pydantic import BaseModel, ValidationError

from src.loaders.generic import load_yaml_config

# =============================================================================
# TEST CONFIG CLASSES
# =============================================================================


class SimpleConfig(BaseModel):
    """Simple test configuration."""
    name: str
    value: int
    enabled: bool = True


class NestedConfig(BaseModel):
    """Nested test configuration."""
    name: str
    settings: SimpleConfig
    tags: list[str] = []


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def simple_yaml_file(tmp_path):
    """Create a simple YAML file for testing."""
    yaml_file = tmp_path / "simple_config.yaml"
    
    config_data = {
        "name": "test_config",
        "value": 42,
        "enabled": True
    }
    
    with open(yaml_file, 'w') as f:
        yaml.dump(config_data, f)
    
    return yaml_file


@pytest.fixture
def nested_yaml_file(tmp_path):
    """Create a nested YAML file for testing."""
    yaml_file = tmp_path / "nested_config.yaml"
    
    config_data = {
        "name": "nested_test",
        "settings": {
            "name": "inner_config",
            "value": 100,
            "enabled": False
        },
        "tags": ["tag1", "tag2", "tag3"]
    }
    
    with open(yaml_file, 'w') as f:
        yaml.dump(config_data, f)
    
    return yaml_file


@pytest.fixture
def timeframe_yaml_file(tmp_path):
    """Create a timeframe YAML file for testing."""
    yaml_file = tmp_path / "timeframe_config.yaml"
    
    config_data = {
        "name": "timeframe_test",
        "supported_timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        "native_timeframe": "1m",
        "resample_strategy": {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        }
    }
    
    with open(yaml_file, 'w') as f:
        yaml.dump(config_data, f)
    
    return yaml_file


@pytest.fixture
def complex_yaml_file(tmp_path):
    """Create a complex YAML file for testing."""
    yaml_file = tmp_path / "complex_config.yaml"
    
    config_data = {
        "name": "complex_test",
        "version": "1.0.0",
        "settings": {
            "cache_enabled": True,
            "max_retries": 3,
            "timeout": 30
        },
        "timeframes": {
            "name": "timeframe_config",
            "supported_timeframes": ["1m", "5m", "15m"],
            "native_timeframe": "1m",
            "resample_strategy": {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }
        },
        "metadata": {
            "author": "test_user",
            "created": "2024-01-01",
            "description": "Test configuration"
        }
    }
    
    with open(yaml_file, 'w') as f:
        yaml.dump(config_data, f)
    
    return yaml_file


# =============================================================================
# BASIC LOADER TESTS
# =============================================================================

def test_load_yaml_config_raw(simple_yaml_file):
    """Test loading YAML config without validation."""
    config = load_yaml_config(simple_yaml_file)
    
    assert isinstance(config, dict)
    assert config["name"] == "test_config"
    assert config["value"] == 42
    assert config["enabled"] is True


def test_load_yaml_config_with_simple_validation(simple_yaml_file):
    """Test loading YAML config with simple Pydantic validation."""
    config = load_yaml_config(simple_yaml_file, SimpleConfig)
    
    assert isinstance(config, SimpleConfig)
    assert config.name == "test_config"
    assert config.value == 42
    assert config.enabled is True


def test_load_yaml_config_with_nested_validation(nested_yaml_file):
    """Test loading YAML config with nested Pydantic validation."""
    config = load_yaml_config(nested_yaml_file, NestedConfig)
    
    assert isinstance(config, NestedConfig)
    assert config.name == "nested_test"
    assert isinstance(config.settings, SimpleConfig)
    assert config.settings.name == "inner_config"
    assert config.settings.value == 100
    assert config.settings.enabled is False
    assert config.tags == ["tag1", "tag2", "tag3"]


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

def test_load_yaml_config_nonexistent_file(tmp_path):
    """Test loading from non-existent YAML file."""
    nonexistent_file = tmp_path / "nonexistent.yaml"
    
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_yaml_config(nonexistent_file)


def test_load_yaml_config_invalid_yaml(tmp_path):
    """Test loading invalid YAML file."""
    invalid_yaml = tmp_path / "invalid.yaml"
    
    with open(invalid_yaml, 'w') as f:
        f.write("invalid: yaml: content: [")
    
    with pytest.raises(ValueError, match="Invalid YAML"):
        load_yaml_config(invalid_yaml)


def test_load_yaml_config_validation_error(simple_yaml_file):
    """Test loading YAML with validation errors."""
    # Modify YAML to have invalid data
    with open(simple_yaml_file, 'w') as f:
        yaml.dump({"invalid_field": "invalid_value"}, f)
    
    with pytest.raises(ValidationError):
        load_yaml_config(simple_yaml_file, SimpleConfig)


def test_load_yaml_config_missing_required_field(simple_yaml_file):
    """Test loading YAML with missing required fields."""
    # Modify YAML to remove required field
    with open(simple_yaml_file, 'w') as f:
        yaml.dump({"value": 42, "enabled": True}, f)  # Missing 'name'
    
    with pytest.raises(ValidationError):
        load_yaml_config(simple_yaml_file, SimpleConfig)


def test_load_yaml_config_wrong_field_type(simple_yaml_file):
    """Test loading YAML with wrong field types."""
    # Modify YAML to have wrong type
    with open(simple_yaml_file, 'w') as f:
        yaml.dump({"name": "test", "value": "not_a_number", "enabled": True}, f)
    
    with pytest.raises(ValidationError):
        load_yaml_config(simple_yaml_file, SimpleConfig)


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

def test_load_yaml_config_empty_file(tmp_path):
    """Test loading empty YAML file."""
    empty_yaml = tmp_path / "empty.yaml"
    
    # Create empty file
    empty_yaml.touch()
    
    config = load_yaml_config(empty_yaml)
    
    # Should return None for empty file
    assert config is None


def test_load_yaml_config_with_comments(tmp_path):
    """Test loading YAML with comments."""
    yaml_file = tmp_path / "commented.yaml"
    
    yaml_content = """
# This is a comment
name: test_config
# Another comment
value: 42
# Inline comment
enabled: true  # This is enabled
"""
    
    with open(yaml_file, 'w') as f:
        f.write(yaml_content)
    
    config = load_yaml_config(yaml_file, SimpleConfig)
    
    assert config.name == "test_config"
    assert config.value == 42
    assert config.enabled is True


def test_load_yaml_config_with_anchors_and_aliases(tmp_path):
    """Test loading YAML with anchors and aliases."""
    yaml_file = tmp_path / "anchors.yaml"
    
    yaml_content = """
defaults: &defaults
  value: 30
  enabled: true

config1:
  <<: *defaults
  name: "config1"

config2:
  <<: *defaults
  name: "config2"
  value: 60  # Override default
"""
    
    with open(yaml_file, 'w') as f:
        f.write(yaml_content)
    
    config = load_yaml_config(yaml_file)
    
    assert config["config1"]["value"] == 30
    assert config["config1"]["enabled"] is True
    assert config["config1"]["name"] == "config1"
    assert config["config2"]["value"] == 60  # Overridden
    assert config["config2"]["enabled"] is True   # Inherited
    assert config["config2"]["name"] == "config2"


def test_load_yaml_config_with_nested_structure(tmp_path):
    """Test loading YAML with deeply nested structures."""
    yaml_file = tmp_path / "deep_nested.yaml"
    
    nested_data = {
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "value": "deep_value"
                    }
                }
            }
        },
        "array": [
            {"item": 1, "nested": {"value": "a"}},
            {"item": 2, "nested": {"value": "b"}},
            {"item": 3, "nested": {"value": "c"}}
        ]
    }
    
    with open(yaml_file, 'w') as f:
        yaml.dump(nested_data, f)
    
    config = load_yaml_config(yaml_file)
    
    assert config["level1"]["level2"]["level3"]["level4"]["value"] == "deep_value"
    assert len(config["array"]) == 3
    assert config["array"][0]["item"] == 1
    assert config["array"][0]["nested"]["value"] == "a"


def test_load_yaml_config_with_special_values(tmp_path):
    """Test loading YAML with special values (null, empty strings, etc.)."""
    yaml_file = tmp_path / "special_values.yaml"
    
    special_data = {
        "null_value": None,
        "empty_string": "",
        "zero_value": 0,
        "false_value": False,
        "empty_list": [],
        "empty_dict": {},
        "special_chars": "!@#$%^&*()",
        "unicode": "café résumé naïve"
    }
    
    with open(yaml_file, 'w') as f:
        yaml.dump(special_data, f)
    
    config = load_yaml_config(yaml_file)
    
    assert config["null_value"] is None
    assert config["empty_string"] == ""
    assert config["zero_value"] == 0
    assert config["false_value"] is False
    assert config["empty_list"] == []
    assert config["empty_dict"] == {}
    assert config["special_chars"] == "!@#$%^&*()"
    assert config["unicode"] == "café résumé naïve"