from unittest.mock import MagicMock, patch

import pytest

from models.system import StrategyStepTemplate

pytest.skip("Skipping all tests in this file for now", allow_module_level=True)


def test_registry_loader_loads_templates():
    """Should load templates from YAML file."""
    # Arrange
    mock_yaml_content = """
    steps:
      detect_trend:
        pure_function: "utils.get_trend"
        context_inputs: "{}"
        context_outputs: "{'trend': 'direction'}"
        config_mapping: "{}"
    """
    
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = mock_yaml_content
        
        # Act
        loader = RegistryLoader("dummy_path.yaml")
        loader.load_registry()
        
        # Assert
        template = loader.get_template("detect_trend")
        assert isinstance(template, StrategyStepTemplate)
        assert template.pure_function == "utils.get_trend"
        assert template.context_outputs == "{'trend': 'direction'}"


def test_registry_loader_raises_on_missing_template():
    """Should raise KeyError when template not found."""
    # Arrange
    loader = RegistryLoader("dummy_path.yaml")
    loader.load_registry()
    
    # Act & Assert
    with pytest.raises(KeyError):
        loader.get_template("non_existent")


def test_registry_loader_lists_available_templates():
    """Should list all available template IDs."""
    # Arrange
    mock_yaml_content = """
    steps:
      detect_trend:
        pure_function: "utils.get_trend"
        context_inputs: "{}"
        context_outputs: "{}"
        config_mapping: "{}"
      find_extreme:
        pure_function: "utils.find_extreme"
        context_inputs: "{}"
        context_outputs: "{}"
        config_mapping: "{}"
    """
    
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = mock_yaml_content
        
        # Act
        loader = RegistryLoader("dummy_path.yaml")
        loader.load_registry()
        
        # Assert
        templates = loader.list_available_templates()
        assert set(templates) == {"detect_trend", "find_extreme"} 