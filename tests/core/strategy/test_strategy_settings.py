"""Tests for StrategySettings."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from core.strategy.settings import StrategySettings


def test_strategy_settings_defaults():
    """Test StrategySettings with default values."""
    settings = StrategySettings()
    assert settings.config_dir == Path("configs/strategies")
    assert isinstance(settings.config_dir, Path)

def test_strategy_settings_with_custom_config_dir():
    """Test StrategySettings with custom config directory."""
    custom_dir = Path("custom/strategies")
    settings = StrategySettings(config_dir=custom_dir)
    assert settings.config_dir == custom_dir
    assert isinstance(settings.config_dir, Path)
