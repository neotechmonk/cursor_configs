"""Tests for trading session implementations."""

from decimal import Decimal
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from core.price_feeds import YahooFinanceProvider
from core.session import SimpleTradingSession

from core.portfolio import SimplePortfolio
from core.protocols import SymbolConfig, Timeframe


@pytest.fixture
def portfolio():
    return SimplePortfolio(
        name="test_portfolio",
        initial_capital=Decimal("100000"),
        risk_limits={
            "max_position_size": Decimal("10000"),
            "max_drawdown": Decimal("0.1"),
        }
    )


@pytest.fixture
def mock_price_data():
    """Create mock price data for testing."""
    return pd.DataFrame({
        'Open': [100, 101, 102],
        'High': [105, 106, 107],
        'Low': [95, 96, 97],
        'Close': [102, 103, 104]
    }, index=pd.date_range(start='2024-01-01', periods=3))


@pytest.fixture
def mock_yfinance(mock_price_data):
    """Mock yfinance.Ticker with test data."""
    with patch('yfinance.Ticker') as mock:
        mock_ticker = Mock()
        mock_ticker.info = {"regularMarketPrice": 150.0}
        mock_ticker.history.return_value = mock_price_data
        mock.return_value = mock_ticker
        yield mock


@pytest.fixture
def yahoo_provider(mock_yfinance):
    """Create a YahooFinanceProvider with mocked yfinance."""
    return YahooFinanceProvider({"api_key": "test"})


@pytest.fixture
def trading_session(portfolio, yahoo_provider):
    """Create a trading session with test configuration."""
    return SimpleTradingSession(
        name="test_session",
        symbols={
            "AAPL": SymbolConfig(
                symbol="AAPL",
                price_feed="yahoo",
                timeframe=Timeframe.D1,
                feed_config={"cache_duration": "1h"}
            )
        },
        portfolio=portfolio,
        price_feeds={"yahoo": yahoo_provider}
    )


def test_trading_session_initialization(trading_session):
    """Test trading session initialization."""
    assert trading_session.name == "test_session"
    assert "AAPL" in trading_session.symbols
    assert isinstance(trading_session.portfolio, SimplePortfolio)


def test_trading_session_get_price_data(trading_session, mock_yfinance, mock_price_data):
    """Test getting price data for a symbol."""
    df = trading_session.get_price_data("AAPL")
    
    # Verify the data
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ["Open", "High", "Low", "Close"])
    pd.testing.assert_frame_equal(df, mock_price_data)
    
    # Verify the mock was called correctly
    mock_yfinance.return_value.history.assert_called_once()


def test_trading_session_invalid_symbol(trading_session):
    """Test getting price data for an invalid symbol."""
    with pytest.raises(ValueError, match="Symbol INVALID not configured in session test_session"):
        trading_session.get_price_data("INVALID")


def test_trading_session_invalid_price_feed(trading_session):
    """Test getting price data with an invalid price feed."""
    trading_session.symbols["AAPL"].price_feed = "invalid"
    with pytest.raises(ValueError, match="Price feed invalid not available for symbol AAPL"):
        trading_session.get_price_data("AAPL")


def test_trading_session_multiple_symbols(trading_session, mock_yfinance, mock_price_data):
    """Test getting price data for multiple symbols."""
    # Add another symbol
    trading_session.symbols["MSFT"] = SymbolConfig(
        symbol="MSFT",
        price_feed="yahoo",
        timeframe=Timeframe.D1,
        feed_config={"cache_duration": "1h"}
    )
    
    # Test both symbols
    aapl_data = trading_session.get_price_data("AAPL")
    msft_data = trading_session.get_price_data("MSFT")
    
    # Verify the data
    assert isinstance(aapl_data, pd.DataFrame)
    assert isinstance(msft_data, pd.DataFrame)
    assert not aapl_data.empty
    assert not msft_data.empty
    
    # Verify the data matches our mock
    pd.testing.assert_frame_equal(aapl_data, mock_price_data)
    pd.testing.assert_frame_equal(msft_data, mock_price_data)
    
    # Verify the mock was called twice (once for each symbol)
    assert mock_yfinance.return_value.history.call_count == 2 