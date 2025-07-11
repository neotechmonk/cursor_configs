from unittest.mock import patch

import pytest

from core.strategy.steps.container import StrategyStepContainer
from core.strategy.steps.model import StrategyStepDefinition
from core.strategy.steps.settings import StrategyStepSettings


@pytest.fixture
def mock_steps() -> list[StrategyStepDefinition]:
    """Mock list of strategy steps."""
    return [
        StrategyStepDefinition(
            id="detect_trend",
            function_path="src.utils.get_trend",
            input_bindings={},
            output_bindings={"trend": {"mapping": "_"}}
        ),
        StrategyStepDefinition(
            id="find_extreme",
            function_path="src.utils.is_extreme_bar",
            input_bindings={"trend": {"source": "runtime", "mapping": "trend"}},
            output_bindings={"is_extreme": {"mapping": "_"}}
        )
    ]


def test_strategy_step_container_with_mocked_yaml(mock_steps):
    """Test StrategyStepContainer loads mock steps without reading YAML."""

    # Setup settings (actual path won't be used due to patching)
    fake_path = "dummy/path.yaml"
    settings = StrategyStepSettings(config_path=fake_path)

    with patch("core.strategy.steps.container.load_yaml_config", return_value=[step.model_dump() for step in mock_steps]):
        container = StrategyStepContainer(settings=settings)
        steps = container.strategy_steps()

    assert isinstance(steps, list)
    assert all(isinstance(step, StrategyStepDefinition) for step in steps)
    assert steps[0].id == "detect_trend"
    assert steps[1].function_path == "src.utils.is_extreme_bar"


def test_cache_singleton_instance():
    container = StrategyStepContainer(settings=StrategyStepSettings(config_path="fake/path.yaml"))

    cache_1 = container.cache_backend()
    cache_2 = container.cache_backend()

    assert cache_1 is cache_2  # Singleton check
    assert hasattr(cache_1, "add")  # Interface presence check (optional)


def test_scoped_cache_namespace_binding():
    container = StrategyStepContainer(settings=StrategyStepSettings(config_path="fake/path.yaml"))
    scoped_cache = container.cache()

    assert scoped_cache._namespace == "strategy_steps"


# Assuming StrategyStepService accepts 'steps' and 'cache' as args


def test_strategy_step_service_wiring(monkeypatch, mock_steps):
        monkeypatch.setattr("core.strategy.steps.container.load_yaml_config", lambda *a, **kw: [s.model_dump() for s in mock_steps])

        container = StrategyStepContainer(settings=StrategyStepSettings(config_path="fake/path.yaml"))

        container.init_resources()  
        service = container.service()
        assert service.get("detect_trend") == mock_steps[0]
        assert service.get_all() == mock_steps