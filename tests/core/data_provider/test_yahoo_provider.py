"""Tests for Yahoo Finance price feed provider."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests
from curl_cffi.requests.exceptions import DNSError

from core.data_provider.config import PricefeedTimeframeConfig
from core.data_provider.error import SymbolError, TimeframeError
from core.data_provider.resampler import ResampleStrategy
from core.data_provider.providers.yahoo import YahooFinanceConfig, YahooFinanceProvider
from core.time import CustomTimeframe


@pytest.fixture
def yahoo_time_config():
    """Create a test configuration for Yahoo Finance price feed provider."""
    return PricefeedTimeframeConfig(
        supported_timeframes={
            CustomTimeframe("1d"),
            CustomTimeframe("1h"),
            CustomTimeframe("5m"),
        },
        native_timeframe=CustomTimeframe("1d"),
        resample_strategy=ResampleStrategy(
            open="first",
            high="max",
            low="min",
            close="last",
            volume="sum"
        )
    )


@pytest.fixture
def yahoo_config(yahoo_time_config):
    """Create a test configuration for Yahoo Finance price feed provider."""
    return YahooFinanceConfig(
        name="yahoo",
        timeframes={
            "supported_timeframes": ["1d", "1h", "5m"],
            "native_timeframe": "1d",
            "resample_strategy": {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }
        },
        api_key=None,
        cache_duration="1h"
    )


@pytest.fixture
def mock_ticker_data():
    """Create mock ticker data for testing."""
    dates = pd.date_range(start='2024-01-01', periods=10, freq='1d')
    data = {
        'Open': [100.0 + i * 0.1 for i in range(10)],
        'High': [100.5 + i * 0.1 for i in range(10)],
        'Low': [99.5 + i * 0.1 for i in range(10)],
        'Close': [100.2 + i * 0.1 for i in range(10)],
        'Volume': [1000000 + i * 10000 for i in range(10)]
    }
    df = pd.DataFrame(data, index=dates)
    # Ensure the index name is 'Date' to match yfinance behavior
    df.index.name = 'Date'
    return df


@pytest.fixture
def mock_ticker_info():
    """Create mock ticker info for testing."""
    return {
        'regularMarketPrice': 100.25,
        'symbol': 'AAPL',
        'shortName': 'Apple Inc.',
        'marketCap': 3000000000000
    }


def test_yahoo_time_config(yahoo_time_config):
    """Test that PricefeedTimeframeConfig can be created with custom objects."""
    conf = yahoo_time_config
    
    # Test that the configuration was created successfully
    assert len(conf.supported_timeframes) == 3
    assert conf.native_timeframe == CustomTimeframe("1d")
    assert conf.resample_strategy.open == "first"
    assert conf.resample_strategy.high == "max"
    assert conf.resample_strategy.low == "min"
    assert conf.resample_strategy.close == "last"
    assert conf.resample_strategy.volume == "sum"
    
    # Test that all expected timeframes are present
    expected_timeframes = {
        CustomTimeframe("1d"),
        CustomTimeframe("1h"),
        CustomTimeframe("5m"),
    }
    
    for tf in expected_timeframes:
        assert tf in conf.supported_timeframes


def test_yahoo_provider_initialization(yahoo_config):
    """Test Yahoo Finance price feed provider initialization."""
    provider = YahooFinanceProvider(yahoo_config)
    
    assert provider.name == "yahoo"
    assert len(provider.timeframes) == 3
    assert CustomTimeframe("1d") in provider.timeframes
    assert CustomTimeframe("1h") in provider.timeframes
    assert CustomTimeframe("5m") in provider.timeframes


@patch('yfinance.Ticker')
def test_yahoo_provider_get_price_data_mocked(mock_ticker_class, yahoo_config, mock_ticker_data, mock_ticker_info):
    """Test getting price data with mocked Yahoo Finance."""
    # Setup mock
    mock_ticker = Mock()
    mock_ticker.info = mock_ticker_info
    mock_ticker.history.return_value = mock_ticker_data
    mock_ticker_class.return_value = mock_ticker
    
    provider = YahooFinanceProvider(yahoo_config)
    
    # Test getting data
    df = provider.get_price_data(
        symbol="AAPL",
        timeframe=CustomTimeframe("1d")
    )
    
    # Verify the result
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 10
    assert 'timestamp' in df.columns
    assert 'open' in df.columns
    assert 'high' in df.columns
    assert 'low' in df.columns
    assert 'close' in df.columns
    assert 'volume' in df.columns
    
    # Verify column names are lowercase
    assert all(col.islower() for col in df.columns)
    
    # Verify mock was called correctly
    mock_ticker_class.assert_called_once_with("AAPL")
    mock_ticker.history.assert_called_once()


@patch('yfinance.Ticker')
def test_yahoo_provider_invalid_symbol_mocked(mock_ticker_class, yahoo_config):
    """Test handling of invalid symbol with mocked Yahoo Finance."""
    # Setup mock for invalid symbol
    mock_ticker = Mock()
    mock_ticker.info = {}  # Empty info indicates invalid symbol
    mock_ticker_class.return_value = mock_ticker
    
    provider = YahooFinanceProvider(yahoo_config)
    
    # Test that invalid symbol raises SymbolError
    with pytest.raises(SymbolError, match="Symbol INVALID not found or invalid"):
        provider.get_price_data(
            symbol="INVALID",
            timeframe=CustomTimeframe("1d")
        )


@patch('yfinance.Ticker')
def test_yahoo_provider_no_data_mocked(mock_ticker_class, yahoo_config, mock_ticker_info):
    """Test handling of symbol with no data with mocked Yahoo Finance."""
    # Setup mock for symbol with no data
    mock_ticker = Mock()
    mock_ticker.info = mock_ticker_info
    mock_ticker.history.return_value = pd.DataFrame()  # Empty DataFrame
    mock_ticker_class.return_value = mock_ticker
    
    provider = YahooFinanceProvider(yahoo_config)
    
    # Test that symbol with no data raises SymbolError
    with pytest.raises(SymbolError, match="No data available for symbol AAPL"):
        provider.get_price_data(
            symbol="AAPL",
            timeframe=CustomTimeframe("1d")
        )


def test_yahoo_provider_unsupported_timeframe(yahoo_config):
    """Test handling of unsupported timeframe."""
    provider = YahooFinanceProvider(yahoo_config)
    
    # Test that unsupported timeframe raises TimeframeError
    with pytest.raises(TimeframeError, match="Timeframe 1m not supported"):
        provider.get_price_data(
            symbol="AAPL",
            timeframe=CustomTimeframe("1m")
        )


@patch('yfinance.Ticker')
def test_yahoo_provider_validate_symbol_mocked(mock_ticker_class, yahoo_config, mock_ticker_info):
    """Test symbol validation with mocked Yahoo Finance."""
    # Setup mock
    mock_ticker = Mock()
    mock_ticker.info = mock_ticker_info
    mock_ticker_class.return_value = mock_ticker
    
    provider = YahooFinanceProvider(yahoo_config)
    
    # Test valid symbol
    assert provider.validate_symbol("AAPL") is True
    
    # Test invalid symbol
    mock_ticker.info = {}
    assert provider.validate_symbol("INVALID") is False


@patch('yfinance.Ticker')
def test_yahoo_provider_validate_symbol_exception_mocked(mock_ticker_class, yahoo_config):
    """Test symbol validation when exception occurs."""
    # Setup mock to raise exception
    mock_ticker_class.side_effect = Exception("Network error")
    
    provider = YahooFinanceProvider(yahoo_config)
    
    # Test that exception is handled gracefully
    assert provider.validate_symbol("AAPL") is False


@patch('yfinance.Ticker')
def test_yahoo_provider_time_range_filtering(mock_ticker_class, yahoo_config, mock_ticker_data, mock_ticker_info):
    """Test time range filtering with mocked Yahoo Finance."""
    # Setup mock
    mock_ticker = Mock()
    mock_ticker.info = mock_ticker_info
    mock_ticker.history.return_value = mock_ticker_data
    mock_ticker_class.return_value = mock_ticker
    
    provider = YahooFinanceProvider(yahoo_config)
    
    start_time = datetime(2024, 1, 1)
    end_time = datetime(2024, 1, 5)
    
    # Test getting data with time range
    df = provider.get_price_data(
        symbol="AAPL",
        timeframe=CustomTimeframe("1d"),
        start_time=start_time,
        end_time=end_time
    )
    
    # Verify mock was called with time range
    mock_ticker.history.assert_called_once_with(
        start=start_time,
        end=end_time,
        interval='1d'
    )


@patch('yfinance.Ticker')
def test_yahoo_provider_with_api_key(mock_ticker_class, yahoo_time_config):
    """Test Yahoo Finance provider with API key."""
    config = YahooFinanceConfig(
        name="yahoo",
        timeframes=yahoo_time_config,
        api_key="test_api_key",
        cache_duration="1h"
    )
    
    # yfinance doesn't use API keys, so we just test that initialization works
    provider = YahooFinanceProvider(config)
    assert provider.name == "yahoo"
    assert provider._config.api_key == "test_api_key"


# Live tests (will be skipped if no internet connection)
def check_yahoo_connectivity():
    """Check if Yahoo Finance is reachable."""
    urls_to_test = [
        "https://finance.yahoo.com",
        "https://query1.finance.yahoo.com"
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except ( requests.RequestException, DNSError , Exception) :
            continue
    return False
    

@pytest.mark.live
@pytest.mark.skipif(
    not check_yahoo_connectivity(), reason="Internet connection required to reach yahoo.com")
def test_yahoo_provider_live_validation():
    """Test Yahoo Finance provider with live data (requires internet)."""
    config = YahooFinanceConfig(
        name="yahoo",
        timeframes={
            "supported_timeframes": ["1d"],
            "native_timeframe": "1d",
            "resample_strategy": {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }
        },
        api_key=None,
        cache_duration="1h"
    )
    
    provider = YahooFinanceProvider(config)
    
    # Test with a well-known symbol
    assert provider.validate_symbol("AAPL") is True
    assert provider.validate_symbol("MSFT") is True
    assert provider.validate_symbol("INVALID_SYMBOL_12345") is False


@pytest.mark.live
def test_yahoo_provider_live_data():
    """Test getting live data from Yahoo Finance (requires internet)."""
    config = YahooFinanceConfig(
        name="yahoo",
        timeframes={
            "supported_timeframes": ["1d"],
            "native_timeframe": "1d",
            "resample_strategy": {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }
        },
        api_key=None,
        cache_duration="1h"
    )
    
    provider = YahooFinanceProvider(config)
    
    # Test getting recent data
    end_time = datetime.now().replace(tzinfo=None)
    start_time = end_time - timedelta(days=7)
    
    df = provider.get_price_data(
        symbol="AAPL",
        timeframe=CustomTimeframe("1d"),
        start_time=start_time,
        end_time=end_time
    )
    
    # Verify the result
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'timestamp' in df.columns
    assert 'open' in df.columns
    assert 'high' in df.columns
    assert 'low' in df.columns
    assert 'close' in df.columns
    assert 'volume' in df.columns
    

@pytest.mark.live
def test_yahoo_provider_live_error_handling():
    """Test error handling with live data (requires internet)."""
    config = YahooFinanceConfig(
        name="yahoo",
        timeframes={
            "supported_timeframes": ["1d"],
            "native_timeframe": "1d",
            "resample_strategy": {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }
        },
        api_key=None,
        cache_duration="1h"
    )
    
    provider = YahooFinanceProvider(config)
    
    # Test with invalid symbol
    with pytest.raises(SymbolError):
        provider.get_price_data(
            symbol="INVALID_SYMBOL_12345",
            timeframe=CustomTimeframe("1d")
        )
    
    # Test with unsupported timeframe
    with pytest.raises(TimeframeError):
        provider.get_price_data(
            symbol="AAPL",
            timeframe=CustomTimeframe("1m")  # Not in supported timeframes
        ) 