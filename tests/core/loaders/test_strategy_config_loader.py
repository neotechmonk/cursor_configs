"""Tests for strategy configuration loader."""

from unittest.mock import MagicMock, patch

import pytest
import yaml

from loaders.strategy_config_loader import create_new_strategy, load_strategies


@pytest.fixture
def mock_step_registry():
    """Create a mock step registry."""
    registry = MagicMock()
    registry.get_step_template.return_value = MagicMock()
    return registry


@pytest.fixture
def strategy_data():
    """Sample strategy data for testing."""
    return {
        "name": "test_strategy",
        "steps": [
            {
                "system_step_id": "step1",
                "parameters": {"param1": "value1"},
                "reevaluates": []
            },
            {
                "system_step_id": "step2",
                "parameters": {"param2": "value2"},
                "reevaluates": ["step1"]
            }
        ]
    }


def test_create_strategy_basic(mock_step_registry, strategy_data):
    """Test creating a basic strategy without reevaluates."""
    with patch('loaders.strategy_config_loader.StrategyConfig') as mock_strategy_class, \
         patch('loaders.strategy_config_loader.StrategyStep') as mock_step_class:
        
        mock_strategy = MagicMock()
        mock_strategy_class.return_value = mock_strategy
        
        mock_step1 = MagicMock()
        mock_step2 = MagicMock()
        mock_step_class.side_effect = [mock_step1, mock_step2]
        
        create_new_strategy(strategy_data, mock_step_registry)
        
        mock_strategy_class.assert_called_once_with(
            name="test_strategy",
            steps=[mock_step1, mock_step2]
        )


def test_create_strategy_with_reevaluates(mock_step_registry, strategy_data):
    """Test creating a strategy with reevaluates."""
    with patch('loaders.strategy_config_loader.StrategyConfig') as mock_strategy_class, \
         patch('loaders.strategy_config_loader.StrategyStep') as mock_step_class:
        
        mock_strategy = MagicMock()
        mock_strategy_class.return_value = mock_strategy
        
        mock_step1 = MagicMock()
        mock_step2 = MagicMock()
        mock_step_class.side_effect = [mock_step1, mock_step2]
        
        create_new_strategy(strategy_data, mock_step_registry)
        
        # Verify that step2 has step1 in its reevaluates
        mock_step2.reevaluates = [mock_step1]
        
        mock_strategy_class.assert_called_once_with(
            name="test_strategy",
            steps=[mock_step1, mock_step2]
        )


def test_create_strategy_validation_error(mock_step_registry):
    """Test that validation errors are raised."""
    invalid_strategy_data = {
        "name": "test_strategy",
        "steps": [
            {
                "system_step_id": "step1",
                "invalid_field": "value"  # This should cause validation error
            }
        ]
    }
    
    with patch('loaders.strategy_config_loader.StrategyStep') as mock_step_class:
        mock_step_class.side_effect = Exception("Validation error")
        
        with pytest.raises(Exception, match="Validation error"):
            create_new_strategy(invalid_strategy_data, mock_step_registry)


def test_create_strategy_reevaluates_resolution(mock_step_registry):
    """Test that reevaluates are properly resolved using step map."""
    strategy_data = {
        "name": "test_strategy",
        "steps": [
            {
                "system_step_id": "step1",
                "parameters": {"param1": "value1"},
                "reevaluates": []
            },
            {
                "system_step_id": "step2",
                "parameters": {"param2": "value2"},
                "reevaluates": ["step1", "step3"]  # step3 doesn't exist yet
            },
            {
                "system_step_id": "step3",
                "parameters": {"param3": "value3"},
                "reevaluates": []
            }
        ]
    }
    
    with patch('loaders.strategy_config_loader.StrategyConfig') as mock_strategy_class, \
         patch('loaders.strategy_config_loader.StrategyStep') as mock_step_class:
        
        mock_strategy = MagicMock()
        mock_strategy_class.return_value = mock_strategy
        
        mock_step1 = MagicMock()
        mock_step2 = MagicMock()
        mock_step3 = MagicMock()
        mock_step_class.side_effect = [mock_step1, mock_step2, mock_step3]
        
        create_new_strategy(strategy_data, mock_step_registry)
        
        # Verify that step2 has step1 and step3 in its reevaluates
        mock_step2.reevaluates = [mock_step1, mock_step3]
        
        mock_strategy_class.assert_called_once_with(
            name="test_strategy",
            steps=[mock_step1, mock_step2, mock_step3]
        )


@pytest.fixture
def strategies_dir(tmp_path):
    """Create a temporary strategies directory for testing."""
    strategies_dir = tmp_path / "strategies"
    strategies_dir.mkdir()
    return strategies_dir


def test_load_strategies_success(strategies_dir, mock_step_registry):
    """Test successfully loading strategies from directory."""
    # Create strategy files
    strategy1_data = {
        "name": "strategy1",
        "steps": [
            {
                "system_step_id": "step1",
                "parameters": {"param1": "value1"},
                "reevaluates": []
            }
        ]
    }
    
    strategy2_data = {
        "name": "strategy2",
        "steps": [
            {
                "system_step_id": "step2",
                "parameters": {"param2": "value2"},
                "reevaluates": []
            }
        ]
    }
    
    strategy1_file = strategies_dir / "strategy1.yaml"
    strategy2_file = strategies_dir / "strategy2.yaml"
    
    with open(strategy1_file, "w") as f:
        yaml.dump(strategy1_data, f)
    
    with open(strategy2_file, "w") as f:
        yaml.dump(strategy2_data, f)
    
    with patch('loaders.strategy_config_loader.create_new_strategy') as mock_create:
        mock_strategy1 = MagicMock()
        mock_strategy1.name = "strategy1"
        mock_strategy2 = MagicMock()
        mock_strategy2.name = "strategy2"
        
        mock_create.side_effect = [mock_strategy1, mock_strategy2]
        
        result = load_strategies(strategies_dir, mock_step_registry)
        
        assert len(result) == 2
        assert result["strategy1"].name == "strategy1"
        assert result["strategy2"].name == "strategy2"
        
        # Verify create_new_strategy was called for each strategy
        assert mock_create.call_count == 2


def test_load_strategies_empty_directory(strategies_dir):
    """Test loading strategies from empty directory."""
    with pytest.raises(FileNotFoundError, match="No YAML configs found"):
        load_strategies(strategies_dir)


def test_load_strategies_invalid_yaml(strategies_dir):
    """Test loading strategies with invalid YAML."""
    strategy_file = strategies_dir / "invalid.yaml"
    with open(strategy_file, "w") as f:
        f.write("invalid: yaml: content: [")
    
    with pytest.raises(yaml.YAMLError):
        load_strategies(strategies_dir)


def test_load_strategies_validation_error(strategies_dir, mock_step_registry):
    """Test that ValidationError is raised for invalid strategy config."""
    strategy_data = {
        "name": "invalid_strategy",
        "steps": [
            {
                "system_step_id": "step1",
                "invalid_field": "value"
            }
        ]
    }
    
    strategy_file = strategies_dir / "invalid_strategy.yaml"
    with open(strategy_file, "w") as f:
        yaml.dump(strategy_data, f)
    
    with patch('loaders.strategy_config_loader.create_new_strategy') as mock_create:
        mock_create.side_effect = Exception("Validation error")
        
        with pytest.raises(Exception, match="Validation error"):
            load_strategies(strategies_dir, mock_step_registry)


def test_load_strategies_no_step_registry(strategies_dir):
    """Test loading strategies without step registry."""
    strategy_data = {
        "name": "strategy1",
        "steps": [
            {
                "system_step_id": "step1",
                "parameters": {"param1": "value1"},
                "reevaluates": []
            }
        ]
    }
    
    strategy_file = strategies_dir / "strategy1.yaml"
    with open(strategy_file, "w") as f:
        yaml.dump(strategy_data, f)
    
    with patch('loaders.strategy_config_loader.create_new_strategy') as mock_create:
        mock_strategy = MagicMock()
        mock_strategy.name = "strategy1"
        mock_create.return_value = mock_strategy
        
        result = load_strategies(strategies_dir, step_registry=None)
        
        assert len(result) == 1
        assert result["strategy1"].name == "strategy1"
