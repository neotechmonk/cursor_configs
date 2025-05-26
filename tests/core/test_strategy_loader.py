from unittest.mock import MagicMock, patch

import pytest

from src.core.strategy_loader import StrategyLoader
from src.models import StrategyConfig, StrategyStep

pytest.skip("Skipping all tests in this file for now", allow_module_level=True)


def test_strategy_loader_creates_strategy():
    """Should create strategy config from YAML file."""
    # Arrange
    mock_strategy_yaml = """
    name: "Trend Following Strategy"
    steps:
      - id: detect_trend
        name: "Detect Trend"
        description: "Determine market trend"
        config: {}
        reevaluates: []
    """
    
    mock_registry_loader = MagicMock()
    mock_template = MagicMock()
    mock_registry_loader.get_template.return_value = mock_template
    
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = mock_strategy_yaml
        
        # Act
        loader = StrategyLoader(mock_registry_loader)
        strategy = loader.load_strategy("trend_following")
        
        # Assert
        assert isinstance(strategy, StrategyConfig)
        assert strategy.name == "Trend Following Strategy"
        assert len(strategy.steps) == 1
        step = strategy.steps[0]
        assert isinstance(step, StrategyStep)
        assert step.id == "detect_trend"
        assert step.name == "Detect Trend"


def test_strategy_loader_sets_up_reevaluates():
    """Should set up step dependencies correctly."""
    # Arrange
    mock_strategy_yaml = """
    name: "Trend Following Strategy"
    steps:
      - id: detect_trend
        name: "Detect Trend"
        config: {}
        reevaluates: []
      - id: find_extreme
        name: "Find Extreme"
        config: {}
        reevaluates: ["detect_trend"]
    """
    
    mock_registry_loader = MagicMock()
    mock_template = MagicMock()
    mock_registry_loader.get_template.return_value = mock_template
    
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = mock_strategy_yaml
        
        # Act
        loader = StrategyLoader(mock_registry_loader)
        strategy = loader.load_strategy("trend_following")
        
        # Assert
        find_extreme_step = next(s for s in strategy.steps if s.id == "find_extreme")
        assert len(find_extreme_step.reevaluates) == 1
        assert find_extreme_step.reevaluates[0].id == "detect_trend" 