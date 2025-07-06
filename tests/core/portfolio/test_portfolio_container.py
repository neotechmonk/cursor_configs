# tests/core/portfolio/test_portfolio_container.py
"""Tests for PortfolioContainer."""

from unittest.mock import Mock

from dependency_injector import providers

from core.portfolio.container import PortfolioContainer
from core.portfolio.portfolio import PortfolioService, PortfolioSettings


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


def test_get_caches_portfolio(tmp_path, monkeypatch):
    # Setup dummy YAML
    (tmp_path / "demo.yaml").write_text("description: Demo\ninitial_capital: 10000")

    mock_settings = Mock(spec=PortfolioSettings)
    mock_settings.config_dir = tmp_path

    service = PortfolioService(settings=mock_settings, cache={})

    monkeypatch.setattr(
        "core.portfolio.portfolio.load_yaml_config",
        lambda path, model: Mock(description="Demo", initial_capital=10000)
    )

    p1 = service.get("demo")
    p2 = service.get("demo")

    assert p1 is p2