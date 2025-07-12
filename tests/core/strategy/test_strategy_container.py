from unittest.mock import MagicMock, patch

import pytest

from core.strategy.container import StrategyContainer
from core.strategy.model import Strategy, StrategyConfig
from core.strategy.settings import StrategySettings


@pytest.fixture
def fake_strategy_dict():
    return {
        "name": "my_strategy",
        "steps": [
            {
                "id": "check_fib",
                "description": "Check something",
                "config_bindings": {},
                "runtime_bindings": {"some": "input"},
                "reevaluates": []
            }
        ]
    }


@pytest.fixture
def mock_strategy_config() -> StrategyConfig:
    return StrategyConfig.model_construct(
        name="my_strategy",
        steps=[]
    )


@pytest.fixture
def mock_hydrator(mock_strategy_config):
    """Mock hydration function returning a StrategyConfig."""
    def _hydrator(raw, step_service):
        return mock_strategy_config
    return _hydrator


@pytest.fixture
def mock_step_service():
    """Mock step service with no-op get/get_all."""
    service = MagicMock()
    service.get.return_value = None
    service.get_all.return_value = []
    return service


def test_strategy_container_hydration_and_cache(tmp_path, fake_strategy_dict, mock_hydrator, mock_step_service):
    # Create dummy strategy file
    strategy_name = "my_strategy"
    strategy_file = tmp_path / f"{strategy_name}.yaml"
    strategy_file.write_text("placeholder: true")  # Just to satisfy path.exists()

    # Patch load_yaml_config to return our fake dict
    with patch("core.strategy.service.load_yaml_config", return_value=fake_strategy_dict):
        container = StrategyContainer(
            settings=StrategySettings(config_dir=tmp_path)
        )
        container.model_hydration_fn.override(mock_hydrator)
        container.steps_registry.override(mock_step_service)

        service = container.service()

        strategy = service.get(strategy_name)
        assert isinstance(strategy, Strategy)
        assert strategy.config.name == strategy_name

        # Cached now
        from_cache = service.get(strategy_name)
        assert from_cache is strategy  # Cached object

        # get_all should load and cache if missing
        service.cache.clear()
        all_strats = service.get_all()
        assert any(s.config.name == strategy_name for s in all_strats)