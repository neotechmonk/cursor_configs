"""Tests for trading session implementation."""

from decimal import Decimal
from unittest.mock import Mock

import pandas as pd
import pytest

from core.sessions.trading_session import (
    ExecutionLimits,
    SessionConfig,
    SymbolMapping,
    TradingSessionImpl,
)


@pytest.fixture
def sample_session_config():
    """Create a sample session configuration."""
    return SessionConfig(
        name="test_session",
        description="Test trading session", 
        portfolio="test_portfolio",
        capital_allocation=30000.00,
        strategies=["trend_following"],
        execution_limits=ExecutionLimits(
            max_open_positions=3,
            max_order_size=5000.00,
            trading_hours={"start": "09:30", "end": "16:00"}
        ),
        symbol_mapping={
            "AAPL": SymbolMapping(
                data_provider="csv",
                execution_provider="ib", 
                timeframe="5m",
                enabled=True
            ),
            "SPY": SymbolMapping(
                data_provider="yahoo",
                execution_provider="alpaca",
                timeframe="1m", 
                enabled=False
            )
        }
    )


@pytest.fixture
def sample_session_config_yaml(tmp_path):
    """Create a sample session configuration from YAML file."""
    yaml_content = """
    name: test_session
    description: Test trading session
    portfolio: test_portfolio
    capital_allocation: 30000.00
    strategies: 
      - trend_following
    execution_limits:
      max_open_positions: 3
      max_order_size: 5000.00
      trading_hours:
        start: "09:30"
        end: "16:00"
    symbol_mapping:
      AAPL:
        data_provider: csv
        execution_provider: ib
        timeframe: 5m
        enabled: true
      SPY:
        data_provider: yahoo
        execution_provider: alpaca
        timeframe: 1m
        enabled: false
    """
    import yaml
    config_dict = yaml.safe_load(yaml_content)
    return SessionConfig(**config_dict)


@pytest.fixture
def mock_data_providers():
    """Create mock data providers."""
    csv_provider = Mock()
    csv_provider.get_price_data.return_value = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='5min'),
        'open': [100] * 10,
        'high': [101] * 10,
        'low': [99] * 10,
        'close': [100.5] * 10,
        'volume': [1000] * 10
    })
    
    return {
        "csv": csv_provider,
        "yahoo": Mock()
    }


@pytest.fixture
def mock_execution_providers():
    """Create mock execution providers."""
    return {
        "ib": Mock(),
        "alpaca": Mock()
    }


@pytest.fixture
def trading_session(sample_session_config_yaml, mock_data_providers, mock_execution_providers):
    """Create a trading session instance."""
    return TradingSessionImpl(
        config=sample_session_config_yaml,
        data_providers=mock_data_providers,
        execution_providers=mock_execution_providers
    )


@pytest.mark.parametrize("config_fixture", [
    "sample_session_config",
    "sample_session_config_yaml"
])
def test_session_initialization(config_fixture, mock_data_providers, mock_execution_providers, request):
    """Test session initialization with both direct and YAML-loaded configs."""
    config = request.getfixturevalue(config_fixture)
    trading_session = TradingSessionImpl(
        config=config,
        data_providers=mock_data_providers,
        execution_providers=mock_execution_providers
    )
    assert trading_session.name == "test_session"
    assert trading_session.portfolio_name == "test_portfolio"
    assert trading_session.capital_allocation == Decimal('30000.00')
    assert trading_session.strategies == ["trend_following"]


def test_get_symbol_config(trading_session):
    """Test getting symbol configuration."""
    config = trading_session.get_symbol_config("AAPL")
    assert config["data_provider"] == "csv"
    assert config["execution_provider"] == "ib"
    assert config["timeframe"] == "5m"
    assert config["enabled"] is True


def test_get_symbol_config_invalid_symbol(trading_session):
    """Test getting config for invalid symbol."""
    with pytest.raises(ValueError, match="Symbol INVALID not found"):
        trading_session.get_symbol_config("INVALID")


def test_get_price_data(trading_session):
    """Test getting price data."""
    df = trading_session.get_price_data("AAPL")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10
    assert 'timestamp' in df.columns


def test_get_price_data_disabled_symbol(trading_session):
    """Test getting price data for disabled symbol."""
    with pytest.raises(ValueError, match="Symbol SPY is not enabled"):
        trading_session.get_price_data("SPY")


def test_is_symbol_enabled(trading_session):
    """Test symbol enabled status."""
    assert trading_session.is_symbol_enabled("AAPL") is True
    assert trading_session.is_symbol_enabled("SPY") is False
    assert trading_session.is_symbol_enabled("INVALID") is False


def test_get_enabled_symbols(trading_session):
    """Test getting enabled symbols."""
    enabled_symbols = trading_session.get_enabled_symbols()
    assert "AAPL" in enabled_symbols
    assert "SPY" not in enabled_symbols


def test_session_pnl(trading_session):
    """Test session P&L tracking."""
    assert trading_session.get_session_pnl() == Decimal('0.0')
    
    trading_session.update_session_pnl(Decimal('1500.50'))
    assert trading_session.get_session_pnl() == Decimal('1500.50')

