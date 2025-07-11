from unittest.mock import MagicMock, patch

import pytest
import yaml

from core.strategy.model import StrategyConfig
from core.strategy.protocol import StrategyProtocol
from core.strategy.service import StrategyService


@pytest.fixture
def mock_cache():
    return MagicMock()


@pytest.fixture
def mock_steps_service():
    return MagicMock()


@pytest.fixture
def mock_hydration():
    return MagicMock()


@pytest.fixture
def dummy_strategy_instance():
    instance = MagicMock(spec=StrategyProtocol)
    return instance


@pytest.fixture
def dummy_strategy_config():
    return MagicMock(spec=StrategyConfig)


@pytest.fixture
def sample_strategy_data():
    """Reusable strategy data for tests"""
    return {
        "name": "test_strategy",
        "steps": [
            {
                "id": "step1",
                "config_bindings": {},
                "runtime_bindings": {},
                "reevaluates": []
            }
        ]
    }


@pytest.fixture
def strategy_yaml_file(tmp_path, sample_strategy_data):
    """Creates a temporary YAML file with strategy data"""
    strategy_name = sample_strategy_data["name"]
    strategy_yaml_path = tmp_path / f"{strategy_name}.yaml"
    
    with open(strategy_yaml_path, 'w') as f:
        yaml.dump(sample_strategy_data, f, default_flow_style=False, sort_keys=False)
    
    return strategy_yaml_path


def test_get_loads_and_caches_strategy(
    tmp_path, mock_cache, mock_steps_service, mock_hydration, dummy_strategy_instance, dummy_strategy_config, sample_strategy_data
):
    # Arrange
    strategy_name = "test_strategy"
    strategy_yaml_path = tmp_path / f"{strategy_name}.yaml"
    
    # Use PyYAML for proper YAML serialization
    with open(strategy_yaml_path, 'w') as f:
        yaml.dump(sample_strategy_data, f, default_flow_style=False, sort_keys=False)

    mock_cache.get.return_value = None
    mock_hydration.return_value = dummy_strategy_config

    # Patch the Strategy return
    with patch("core.strategy.service.Strategy", return_value=dummy_strategy_instance):
        service = StrategyService(
            config_dir=tmp_path,
            cache=mock_cache,
            model_hydration_fn=mock_hydration,
            steps_registry=mock_steps_service
        )

        # Act
        result = service.get(strategy_name)

        # Assert
        mock_cache.get.assert_called_once_with(strategy_name)
        mock_hydration.assert_called_once()
        mock_cache.add.assert_called_once_with(strategy_name, dummy_strategy_instance)
        assert result is dummy_strategy_instance


def test_get_uses_cached_strategy(
    tmp_path, mock_cache, mock_steps_service, mock_hydration, dummy_strategy_instance
):
    strategy_name = "test_strategy"
    mock_cache.get.return_value = dummy_strategy_instance

    service = StrategyService(
        config_dir=tmp_path,
        cache=mock_cache,
        model_hydration_fn=mock_hydration,
        steps_registry=mock_steps_service
    )

    result = service.get(strategy_name)

    mock_cache.get.assert_called_once_with(strategy_name)
    mock_hydration.assert_not_called()
    mock_cache.add.assert_not_called()
    assert result is dummy_strategy_instance