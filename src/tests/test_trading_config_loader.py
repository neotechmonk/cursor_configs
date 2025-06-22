"""Tests for trading configuration loader."""

from unittest.mock import patch

import pytest

from core.price_feeds import YahooFinanceProvider
from core.protocols import Timeframe
from loaders.trading_config_loader import TradingConfigLoader


@pytest.fixture
def config_path(tmp_path):
    """Create a temporary config file."""
    config = """
    price_feeds:
      yahoo:
        provider: "yahoo"
        config:
          api_key: "test_key"
          cache_duration: "1h"
          supported_timeframes:
            - "1d"
            - "1w"

    portfolio:
      name: "Test Portfolio"
      initial_capital: 100000.00
      risk_limits:
        max_position_size: 10000.00
        max_drawdown: 0.10
        stop_loss_pct: 0.02
        take_profit_pct: 0.04

    trading_sessions:
      main_session:
        name: "Test Session"
        symbols:
          AAPL:
            symbol: "AAPL"
            price_feed: "yahoo"
            timeframe: "1d"
            feed_config:
              cache_duration: "1h"
        portfolio: "Test Portfolio"
        price_feeds:
          - "yahoo"
    """
    config_file = tmp_path / "trading_config.yaml"
    config_file.write_text(config)
    return config_file


def test_load_config(config_path):
    """Test loading configuration from file."""
    loader = TradingConfigLoader(config_path)
    config = loader.load()
    
    # Verify price feeds
    assert "yahoo" in config.price_feeds
    assert config.price_feeds["yahoo"].provider == "yahoo"
    assert config.price_feeds["yahoo"].config["api_key"] == "test_key"
    
    # Verify portfolio
    assert config.portfolio.name == "Test Portfolio"
    assert config.portfolio.initial_capital == 100000.00
    assert config.portfolio.risk_limits.max_position_size == 10000.00
    
    # Verify trading session
    assert "main_session" in config.trading_sessions
    session = config.trading_sessions["main_session"]
    assert session.name == "Test Session"
    assert "AAPL" in session.symbols
    assert session.symbols["AAPL"].symbol == "AAPL"
    assert session.symbols["AAPL"].timeframe == "1d"


def test_create_price_feeds(config_path):
    """Test creating price feed providers."""
    loader = TradingConfigLoader(config_path)
    loader.load()
    
    with patch("yfinance.Ticker") as mock_yfinance:
        feeds = loader.create_price_feeds()
        assert "yahoo" in feeds
        assert isinstance(feeds["yahoo"], YahooFinanceProvider)


def test_create_portfolio(config_path):
    """Test creating portfolio."""
    loader = TradingConfigLoader(config_path)
    loader.load()
    
    portfolio = loader.create_portfolio()
    assert portfolio.name == "Test Portfolio"
    assert portfolio.initial_capital == 100000.00


def test_create_trading_sessions(config_path):
    """Test creating trading sessions."""
    loader = TradingConfigLoader(config_path)
    loader.load()
    
    with patch("yfinance.Ticker") as mock_yfinance:
        price_feeds = loader.create_price_feeds()
        portfolio = loader.create_portfolio()
        
        sessions = loader.create_trading_sessions(price_feeds, portfolio)
        assert "main_session" in sessions
        session = sessions["main_session"]
        
        assert session.name == "Test Session"
        assert "AAPL" in session.symbols
        assert session.symbols["AAPL"].symbol == "AAPL"
        assert session.symbols["AAPL"].timeframe == Timeframe.D1 