"""Tests for portfolio protocols and service."""

from unittest.mock import Mock

import pytest

from core.portfolio.portfolio import PortfolioService, PortfolioSettings
from core.portfolio.protocol import PortfolioProtocol


@pytest.fixture
def mock_settings(tmp_path) -> PortfolioSettings:
    """Fixture for mock PortfolioSettings pointing to temp config dir."""
    # Create demo YAML file(s)
    (tmp_path / "demo.yaml").write_text("description: Demo\ninitial_capital: 10000")
    (tmp_path / "extra.yaml").write_text("description: Extra\ninitial_capital: 5000")

    return PortfolioSettings(config_dir=tmp_path)


@pytest.fixture
def mock_loader(monkeypatch):
    """Monkeypatch the YAML config loader to return predictable mocks."""
    def fake_loader(path, model):
        return Mock(description=path.stem.upper(), initial_capital=99999)
    monkeypatch.setattr("core.portfolio.portfolio.load_yaml_config", fake_loader)


def test_get_loads_and_caches(mock_settings, mock_loader):
    """Test that get() loads a portfolio and caches it."""
    service = PortfolioService(settings=mock_settings, cache={})

    p1 : PortfolioProtocol = service.get("demo") # hot load
    p2 : PortfolioProtocol = service.get("demo") # cached load

    assert p1 is p2  # Same object from cache
    assert "demo" in service.cache


def test_get_all_loads_all(mock_settings, mock_loader):
    """Test that get_all() loads all YAML-defined portfolios."""
    service = PortfolioService(settings=mock_settings, cache={})

    portfolios = service.get_all()

    assert isinstance(portfolios, list)
    assert len(portfolios) == 2
    assert sorted(service.cache.keys()) == ["demo", "extra"]


def test_clear_cache(mock_settings, mock_loader):
    """Test that clear_cache() empties the portfolio cache."""
    service = PortfolioService(settings=mock_settings, cache={})

    service.get("demo")
    assert "demo" in service.cache

    service.clear_cache()
    assert service.cache == {}