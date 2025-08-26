"""Tests for advanced trading configuration loader v2."""

from datetime import timedelta

import pandas as pd
import pytest

from loaders.trading_config_loader_v2 import (
    DummyPriceFeedProvider,
    PortfolioConfig,
    PriceFeedProtocol,
    RiskLimits,
    SymbolConfigModel,
    TradingSessionConfig,
)


def test_dummy_price_feed_provider_init_default_name():
    """Test DummyPriceFeedProvider initialization with default name."""
    provider = DummyPriceFeedProvider()
    
    assert provider.name == "dummy"


def test_dummy_price_feed_provider_init_custom_name():
    """Test DummyPriceFeedProvider initialization with custom name."""
    provider = DummyPriceFeedProvider("CustomProvider")
    
    assert provider.name == "CustomProvider"


def test_dummy_price_feed_provider_get_price_data_returns_dataframe():
    """Test that get_price_data returns a pandas DataFrame."""
    provider = DummyPriceFeedProvider()
    
    result = provider.get_price_data("AAPL", "1d")
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 100  # Should generate 100 periods


def test_dummy_price_feed_provider_get_price_data_columns():
    """Test that get_price_data returns expected columns."""
    provider = DummyPriceFeedProvider()
    result = provider.get_price_data("AAPL", "1d")
    
    expected_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    assert list(result.columns) == expected_columns


def test_dummy_price_feed_provider_get_price_data_timestamp_range():
    """Test that timestamp range is approximately 10 days."""
    provider = DummyPriceFeedProvider()
    result = provider.get_price_data("AAPL", "1d")
    
    start_time = result['timestamp'].min()
    end_time = result['timestamp'].max()
    time_diff = end_time - start_time
    
    # Should be approximately 10 days (allowing for small variations)
    assert timedelta(days=9) <= time_diff <= timedelta(days=11)


def test_dummy_price_feed_provider_get_price_data_price_patterns():
    """Test that price data follows expected patterns."""
    provider = DummyPriceFeedProvider()
    result = provider.get_price_data("AAPL", "1d")
    
    # Base price should be around 100
    assert result['open'].iloc[0] == pytest.approx(100.0, abs=0.1)
    
    # Prices should increase over time
    assert result['open'].iloc[-1] > result['open'].iloc[0]
    
    # High should be higher than low for each row
    assert all(result['high'] >= result['low'])
    
    # High should be higher than open and close
    assert all(result['high'] >= result['open'])
    assert all(result['high'] >= result['close'])


def test_dummy_price_feed_provider_get_price_data_volume_patterns():
    """Test that volume data follows expected patterns."""
    provider = DummyPriceFeedProvider()
    result = provider.get_price_data("AAPL", "1d")
    
    # Volume should start around 1000 and increase
    assert result['volume'].iloc[0] == pytest.approx(1000, abs=10)
    assert result['volume'].iloc[-1] > result['volume'].iloc[0]


def test_dummy_price_feed_provider_get_price_data_symbol_agnostic():
    """Test that get_price_data works with any symbol."""
    provider = DummyPriceFeedProvider()
    
    result1 = provider.get_price_data("AAPL", "1d")
    result2 = provider.get_price_data("GOOGL", "1d")
    result3 = provider.get_price_data("MSFT", "1d")
    
    # All should return similar data structures
    assert len(result1) == len(result2) == len(result3)
    assert list(result1.columns) == list(result2.columns) == list(result3.columns)


def test_dummy_price_feed_provider_get_price_data_timeframe_agnostic():
    """Test that get_price_data works with any timeframe."""
    provider = DummyPriceFeedProvider()
    
    result1 = provider.get_price_data("AAPL", "1m")
    result2 = provider.get_price_data("AAPL", "5m")
    result3 = provider.get_price_data("AAPL", "1h")
    
    # All should return similar data structures
    assert len(result1) == len(result2) == len(result3)
    assert list(result1.columns) == list(result2.columns) == list(result3.columns)


def test_dummy_price_feed_provider_get_price_data_kwargs_ignored():
    """Test that additional kwargs are ignored."""
    provider = DummyPriceFeedProvider()
    result = provider.get_price_data("AAPL", "1d", start_date="2023-01-01", end_date="2023-12-31")
    
    # Should still return the same dummy data
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 100


def test_valid_risk_limits():
    """Test creating valid risk limits."""
    risk_limits = RiskLimits(
        max_position_size=10000.0,
        max_drawdown=0.15,
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )
    
    assert risk_limits.max_position_size == 10000.0
    assert risk_limits.max_drawdown == 0.15
    assert risk_limits.stop_loss_pct == 0.05
    assert risk_limits.take_profit_pct == 0.10


def test_risk_limits_frozen():
    """Test that RiskLimits model is frozen (immutable)."""
    risk_limits = RiskLimits(
        max_position_size=10000.0,
        max_drawdown=0.15,
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )
    
    # Should not be able to modify attributes
    with pytest.raises(Exception):  # Pydantic will raise an error
        risk_limits.max_position_size = 20000.0


def test_risk_limits_zero_values():
    """Test risk limits with zero values."""
    risk_limits = RiskLimits(
        max_position_size=0.0,
        max_drawdown=0.0,
        stop_loss_pct=0.0,
        take_profit_pct=0.0
    )
    
    assert risk_limits.max_position_size == 0.0
    assert risk_limits.max_drawdown == 0.0
    assert risk_limits.stop_loss_pct == 0.0
    assert risk_limits.take_profit_pct == 0.0


def test_price_feed_protocol_runtime_checkable():
    """Test that PriceFeedProtocol is runtime checkable."""
    # This should not raise an error
    assert issubclass(DummyPriceFeedProvider, PriceFeedProtocol)


def test_price_feed_protocol_interface():
    """Test that protocol defines the expected interface."""
    # Check that the protocol has the expected method
    assert hasattr(PriceFeedProtocol, '__subclasshook__')
    
    # Check that DummyPriceFeedProvider implements the protocol
    provider = DummyPriceFeedProvider()
    assert isinstance(provider, PriceFeedProtocol)


def test_valid_symbol_config():
    """Test creating valid symbol configuration."""
    mock_provider = DummyPriceFeedProvider("test_provider")
    
    symbol_config = SymbolConfigModel(
        symbol="AAPL",
        price_feed=mock_provider,
        timeframe="1d"
    )
    
    assert symbol_config.symbol == "AAPL"
    assert symbol_config.price_feed == mock_provider
    assert symbol_config.timeframe == "1d"


def test_symbol_config_frozen():
    """Test that SymbolConfigModel is frozen (immutable)."""
    mock_provider = DummyPriceFeedProvider("test_provider")
    
    symbol_config = SymbolConfigModel(
        symbol="AAPL",
        price_feed=mock_provider,
        timeframe="1d"
    )
    
    # Should not be able to modify attributes
    with pytest.raises(Exception):  # Pydantic will raise an error
        symbol_config.symbol = "GOOGL"


def test_symbol_config_arbitrary_types_allowed():
    """Test that arbitrary types are allowed for price_feed."""
    mock_provider = DummyPriceFeedProvider("test_provider")
    
    # This should work without validation errors
    symbol_config = SymbolConfigModel(
        symbol="AAPL",
        price_feed=mock_provider,
        timeframe="1d"
    )
    
    assert symbol_config.price_feed == mock_provider


def test_valid_portfolio_config():
    """Test creating valid portfolio configuration."""
    risk_limits = RiskLimits(
        max_position_size=10000.0,
        max_drawdown=0.15,
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )
    
    portfolio = PortfolioConfig(
        name="test_portfolio",
        initial_capital=100000.0,
        risk_limits=risk_limits
    )
    
    assert portfolio.name == "test_portfolio"
    assert portfolio.initial_capital == 100000.0
    assert portfolio.risk_limits == risk_limits


def test_portfolio_config_frozen():
    """Test that PortfolioConfig is frozen (immutable)."""
    risk_limits = RiskLimits(
        max_position_size=10000.0,
        max_drawdown=0.15,
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )
    
    portfolio = PortfolioConfig(
        name="test_portfolio",
        initial_capital=100000.0,
        risk_limits=risk_limits
    )
    
    # Should not be able to modify attributes
    with pytest.raises(Exception):  # Pydantic will raise an error
        portfolio.name = "new_name"


def test_valid_trading_session_config():
    """Test creating valid trading session configuration."""
    mock_provider = DummyPriceFeedProvider("test_provider")
    
    symbols = {
        "AAPL": SymbolConfigModel(
            symbol="AAPL",
            price_feed=mock_provider,
            timeframe="1d"
        )
    }
    
    session = TradingSessionConfig(
        name="day_trading",
        symbols=symbols,
        portfolio="main_portfolio"
    )
    
    assert session.name == "day_trading"
    assert session.symbols == symbols
    assert session.portfolio == "main_portfolio"


def test_trading_session_config_frozen():
    """Test that TradingSessionConfig is frozen (immutable)."""
    mock_provider = DummyPriceFeedProvider("test_provider")
    
    symbols = {
        "AAPL": SymbolConfigModel(
            symbol="AAPL",
            price_feed=mock_provider,
            timeframe="1d"
        )
    }
    
    session = TradingSessionConfig(
        name="day_trading",
        symbols=symbols,
        portfolio="main_portfolio"
    )
    
    # Should not be able to modify attributes
    with pytest.raises(Exception):  # Pydantic will raise an error
        session.name = "new_name"


def test_trading_session_config_extra_ignore():
    """Test that extra fields are ignored."""
    mock_provider = DummyPriceFeedProvider("test_provider")
    
    symbols = {
        "AAPL": SymbolConfigModel(
            symbol="AAPL",
            price_feed=mock_provider,
            timeframe="1d"
        )
    }
    
    # This should work even with extra fields
    session = TradingSessionConfig(
        name="day_trading",
        symbols=symbols,
        portfolio="main_portfolio",
        extra_field="should_be_ignored"  # This should be ignored
    )
    
    assert session.name == "day_trading"
    assert session.symbols == symbols
    assert session.portfolio == "main_portfolio"
    # The extra field should not be present
    assert not hasattr(session, 'extra_field')


def test_trading_session_config_arbitrary_types_allowed():
    """Test that arbitrary types are allowed for symbols."""
    mock_provider = DummyPriceFeedProvider("test_provider")
    
    symbols = {
        "AAPL": SymbolConfigModel(
            symbol="AAPL",
            price_feed=mock_provider,
            timeframe="1d"
        )
    }
    
    # This should work without validation errors
    session = TradingSessionConfig(
        name="day_trading",
        symbols=symbols,
        portfolio="main_portfolio"
    )
    
    assert session.symbols == symbols
