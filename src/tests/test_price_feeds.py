"""Tests for price feed implementations."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from core.protocols import PriceFeedProvider, SymbolError, Timeframe, TimeframeError
from src.core.price_feeds import YahooFinanceProvider


@pytest.fixture
def mock_yfinance():
    """Mock yfinance.Ticker."""
    with patch("yfinance.Ticker") as mock:
        # Create mock ticker with info
        ticker = Mock()
        ticker.info = {
            "regularMarketPrice": 100.0,
            "symbol": "AAPL",
        }
        
        # Create mock history data
        mock_df = pd.DataFrame({
            "Open": [100.0],
            "High": [101.0],
            "Low": [99.0],
            "Close": [100.5],
            "Volume": [1000000],
        }, index=[datetime.now()])
        ticker.history.return_value = mock_df
        
        mock.return_value = ticker
        yield mock


@pytest.fixture
def yahoo_provider(mock_yfinance) -> PriceFeedProvider:
    """Create a YahooFinanceProvider instance."""
    return YahooFinanceProvider()


def test_yahoo_provider_initialization(yahoo_provider):
    """Test YahooFinanceProvider initialization."""
    assert yahoo_provider.name == "yahoo_finance"
    assert Timeframe.D1 in yahoo_provider.capabilities.supported_timeframes
    assert Timeframe.W1 in yahoo_provider.capabilities.supported_timeframes
    assert yahoo_provider.capabilities.auth_type is None


def test_yahoo_provider_get_price_data(yahoo_provider, mock_yfinance):
    """Test getting price data from Yahoo Finance."""
    # Test successful data fetch
    df = yahoo_provider.get_price_data(
        symbol="AAPL",
        timeframe=Timeframe.D1,
        start_time=datetime.now() - timedelta(days=7),
        end_time=datetime.now()
    )
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ["Open", "High", "Low", "Close", "Volume"])
    
    # Verify mock was called correctly
    mock_yfinance.assert_called_once_with("AAPL")
    mock_yfinance.return_value.history.assert_called_once()


def test_yahoo_provider_invalid_symbol(yahoo_provider, mock_yfinance):
    """Test handling of invalid symbols."""
    # Configure mock to simulate invalid symbol
    mock_yfinance.return_value.info = {}
    
    with pytest.raises(SymbolError, match="Invalid symbol: INVALID"):
        yahoo_provider.get_price_data(
            symbol="INVALID",
            timeframe=Timeframe.D1
        )


def test_yahoo_provider_unsupported_timeframe(yahoo_provider):
    """Test handling of unsupported timeframes."""
    with pytest.raises(TimeframeError, match="Timeframe 1m not supported"):
        yahoo_provider.get_price_data(
            symbol="AAPL",
            timeframe=Timeframe.M1
        )


def test_yahoo_provider_empty_data(yahoo_provider, mock_yfinance):
    """Test handling of empty data response."""
    # Configure mock to return empty DataFrame
    mock_yfinance.return_value.history.return_value = pd.DataFrame()
    
    with pytest.raises(SymbolError, match="No data available for symbol: AAPL"):
        yahoo_provider.get_price_data(
            symbol="AAPL",
            timeframe=Timeframe.D1
        )


def test_yahoo_provider_default_time_range(yahoo_provider, mock_yfinance):
    """Test default time range handling."""
    yahoo_provider.get_price_data(
        symbol="AAPL",
        timeframe=Timeframe.D1
    )
    
    # Verify mock was called with default time range
    call_args = mock_yfinance.return_value.history.call_args[1]
    assert "start" in call_args
    assert "end" in call_args
    assert isinstance(call_args["start"], datetime)
    assert isinstance(call_args["end"], datetime)
    assert call_args["end"] - call_args["start"] == timedelta(days=365) 