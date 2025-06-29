"""Tests for Yahoo Finance price feed provider."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from core.feed.config import PricefeedTimeframeConfig
from src.core.feed.error import ResampleStrategy, SymbolError, TimeframeError
from src.core.feed.providers.yahoo import YahooFinanceConfig, YahooFinanceProvider
from src.core.time import CustomTimeframe

pytest.skip("Need refactoring to match the CSV provider", allow_module_level=True)


@pytest.fixture
def yahoo_config():
    """Create a test configuration for Yahoo Finance provider."""
    return YahooFinanceConfig(
        name="yahoo",
        api_key=None,
        cache_duration="1h",
        rate_limits={"requests_per_minute": 60, "requests_per_day": 2000},
        timeframes=PricefeedTimeframeConfig(
            supported_timeframes={
                CustomTimeframe("1d"),
                CustomTimeframe("1w"),
            },
            native_timeframe=CustomTimeframe("1d"),
            resample_strategy=ResampleStrategy(
                open="first",
                high="max",
                low="min",
                close="last",
                volume="sum"
            ),
        ),
    )


@patch('yfinance.Ticker')
def test_yahoo_provider_initialization(mock_ticker, yahoo_config):
    """Test Yahoo Finance provider initialization."""
    provider = YahooFinanceProvider(yahoo_config)
    
    assert provider.name == "yahoo"
    assert provider.capabilities.requires_auth is False
    assert provider.capabilities.auth_type is None
    assert len(provider.capabilities.supported_timeframes) == 2
    assert CustomTimeframe("1d") in provider.capabilities.supported_timeframes
    assert CustomTimeframe("1w") in provider.capabilities.supported_timeframes


@patch('yfinance.Ticker')
def test_yahoo_provider_get_price_data(mock_ticker, yahoo_config):
    """Test fetching price data from Yahoo Finance."""
    # Setup mock
    mock_ticker_instance = Mock()
    mock_ticker_instance.info = {"regularMarketPrice": 100.0}
    mock_ticker_instance.history.return_value = pd.DataFrame({
        'Open': [100.0],
        'High': [101.0],
        'Low': [99.0],
        'Close': [100.5],
        'Volume': [1000000],
    }, index=[datetime.now()])
    mock_ticker.return_value = mock_ticker_instance
    
    provider = YahooFinanceProvider(yahoo_config)
    
    # Test with valid symbol and timeframe
    df = provider.get_price_data(
        symbol="AAPL",
        timeframe=CustomTimeframe("1d"),
        start_time=datetime.now() - timedelta(days=7),
        end_time=datetime.now()
    )
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])


@patch('yfinance.Ticker')
def test_yahoo_provider_invalid_symbol(mock_ticker, yahoo_config):
    """Test handling of invalid symbols."""
    # Setup mock to simulate invalid symbol
    mock_ticker_instance = Mock()
    mock_ticker_instance.info = None
    mock_ticker.return_value = mock_ticker_instance
    
    provider = YahooFinanceProvider(yahoo_config)
    
    with pytest.raises(SymbolError):
        provider.get_price_data(
            symbol="INVALID",
            timeframe=CustomTimeframe("1d")
        )


@patch('yfinance.Ticker')
def test_yahoo_provider_unsupported_timeframe(mock_ticker, yahoo_config):
    """Test handling of unsupported timeframes."""
    provider = YahooFinanceProvider(yahoo_config)
    
    with pytest.raises(TimeframeError):
        provider.get_price_data(
            symbol="AAPL",
            timeframe=CustomTimeframe("1h")
        )


@patch('yfinance.Ticker')
def test_yahoo_provider_empty_data(mock_ticker, yahoo_config):
    """Test handling of empty data response."""
    # Setup mock to return empty DataFrame
    mock_ticker_instance = Mock()
    mock_ticker_instance.info = {"regularMarketPrice": 100.0}
    mock_ticker_instance.history.return_value = pd.DataFrame()
    mock_ticker.return_value = mock_ticker_instance
    
    provider = YahooFinanceProvider(yahoo_config)
    
    with pytest.raises(SymbolError):
        provider.get_price_data(
            symbol="AAPL",
            timeframe=CustomTimeframe("1d")
        )


@patch('yfinance.Ticker')
def test_yahoo_provider_default_time_range(mock_ticker, yahoo_config):
    """Test default time range handling."""
    # Setup mock
    mock_ticker_instance = Mock()
    mock_ticker_instance.info = {"regularMarketPrice": 100.0}
    mock_ticker_instance.history.return_value = pd.DataFrame({
        'Open': [100.0],
        'High': [101.0],
        'Low': [99.0],
        'Close': [100.5],
        'Volume': [1000000],
    }, index=[datetime.now()])
    mock_ticker.return_value = mock_ticker_instance
    
    provider = YahooFinanceProvider(yahoo_config)
    
    # Test without specifying time range
    provider.get_price_data(
        symbol="AAPL",
        timeframe=CustomTimeframe("1d")
    )
    
    # Verify mock was called with default time range
    call_args = mock_ticker_instance.history.call_args[1]
    assert "start" in call_args
    assert "end" in call_args
    assert isinstance(call_args["start"], datetime)
    assert isinstance(call_args["end"], datetime)


@patch('yfinance.Ticker')
def test_yahoo_provider_validate_symbol(mock_ticker, yahoo_config):
    """Test symbol validation for Yahoo Finance provider."""
    # Setup mock
    mock_ticker_instance = Mock()
    mock_ticker_instance.info = {"regularMarketPrice": 100.0}
    mock_ticker.return_value = mock_ticker_instance
    
    provider = YahooFinanceProvider(yahoo_config)
    
    assert provider.validate_symbol("AAPL") is True
    
    # Test invalid symbol
    mock_ticker_instance.info = None
    assert provider.validate_symbol("INVALID") is False


@patch('yfinance.Ticker')
def test_yahoo_provider_rate_limit_error(mock_ticker, yahoo_config):
    """Test handling of rate limit errors."""
    # Setup mock to simulate rate limit error
    mock_ticker_instance = Mock()
    mock_ticker_instance.info = {"regularMarketPrice": 100.0}
    mock_ticker_instance.history.side_effect = Exception("rate limit exceeded")
    mock_ticker.return_value = mock_ticker_instance
    
    provider = YahooFinanceProvider(yahoo_config)
    
    with pytest.raises(SymbolError, match="rate limit"):
        provider.get_price_data(
            symbol="AAPL",
            timeframe=CustomTimeframe("1d")
        )


@patch('yfinance.Ticker')
def test_yahoo_provider_column_renaming(mock_ticker, yahoo_config):
    """Test that Yahoo Finance columns are properly renamed."""
    # Setup mock with Yahoo Finance column names
    mock_ticker_instance = Mock()
    mock_ticker_instance.info = {"regularMarketPrice": 100.0}
    mock_ticker_instance.history.return_value = pd.DataFrame({
        'Open': [100.0, 101.0],
        'High': [101.0, 102.0],
        'Low': [99.0, 100.0],
        'Close': [100.5, 101.5],
        'Volume': [1000000, 1100000],
    }, index=[datetime.now(), datetime.now() + timedelta(days=1)])
    mock_ticker.return_value = mock_ticker_instance
    
    provider = YahooFinanceProvider(yahoo_config)
    
    df = provider.get_price_data(
        symbol="AAPL",
        timeframe=CustomTimeframe("1d")
    )
    
    # Verify columns are renamed to lowercase
    expected_columns = ['open', 'high', 'low', 'close', 'volume']
    assert all(col in df.columns for col in expected_columns)
    assert 'Open' not in df.columns  # Original column should not be present 