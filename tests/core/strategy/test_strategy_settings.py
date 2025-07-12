"""Tests for StrategySettings."""

from pathlib import Path

from core.strategy.settings import StrategySettings
from core.strategy.steps.settings import StrategyStepSettings


def test_strategy_settings_defaults():
    """Test StrategySettings with default values."""
    settings = StrategySettings(steps_settings=StrategyStepSettings())
    assert settings.config_dir == Path("configs/strategies")
    assert isinstance(settings.config_dir, Path)


def test_strategy_settings_with_custom_config_dir():
    """Test StrategySettings with custom config directory."""
    custom_dir = Path("custom/strategies")
    settings = StrategySettings(steps_settings=StrategyStepSettings(), config_dir=custom_dir)
    assert settings.config_dir == custom_dir
    assert isinstance(settings.config_dir, Path)
