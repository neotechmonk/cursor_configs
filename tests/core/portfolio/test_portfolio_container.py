# tests/core/portfolio/test_portfolio_container.py
"""Tests for PortfolioContainer."""

from unittest.mock import Mock
import pytest
from dependency_injector import providers

from core.portfolio.container import PortfolioContainer
from core.portfolio.portfolio import PortfolioSettings

def test_portfolio_container_initialization():
    """Test that PortfolioContainer initializes correctly."""
    container = PortfolioContainer()

    # Get the DI-managed cache instance
    cache = container.portfolio_cache()

    assert isinstance(cache, dict)
    assert cache == {}  # Should be empty on initialization


def test_portfolio_container_with_settings_provider():
    """Test that PortfolioContainer accepts settings provider."""
    # Create mock settings
    mock_settings = Mock(spec=PortfolioSettings)
    mock_settings.config_dir = "test/config"
    
    # Create settings provider
    settings_provider = providers.Singleton(lambda: mock_settings)
    
    # # Initialize container with settings provider
    container = PortfolioContainer(settings=settings_provider)
    
    # # Check that settings provider is set
    assert container.settings() == mock_settings

# def test_get_caches_portfolio(monkeypatch, tmp_path):
#     """Test that portfolio is loaded once and cached."""
#     # Create fake YAML
#     yaml_path = tmp_path / "demo.yaml"
#     yaml_path.write_text("description: Demo\ninitial_capital: 10000")

#     # Fake settings with path to YAML
#     mock_settings = Mock(spec=PortfolioSettings)
#     mock_settings.config_dir = tmp_path

#     container = PortfolioContainer(settings=providers.Object(mock_settings))

#     # Patch the loader to spy on it
#     calls = []

#     def fake_loader(path, model_cls):
#         calls.append(str(path))
#         return Mock(description="Demo", initial_capital=10000)

#     monkeypatch.setattr("core.portfolio.container.load_yaml_config", fake_loader)

#     # # Call twice
#     p1 = container.get("demo")
#     p2 = container.get("demo")

#     assert p1 is p2  # same object from cache
#     assert len(calls) == 1