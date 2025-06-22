"""Tests for price feed providers."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.core.feed import (
    CSVPriceFeedConfig,
    CSVPriceFeedProvider,
    PricefeedTimeframeConfig,
    YahooFinanceConfig,
    YahooFinanceProvider,
)
from src.core.protocols import ResampleStrategy, SymbolError, TimeframeError
from src.core.time import CustomTimeframe, TimeframeUnit


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary directory with test data."""
    # Create test data directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Create sample price data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
    data = {
        'timestamp': dates,
        'open': [100 + i * 0.1 for i in range(100)],
        'high': [100.5 + i * 0.1 for i in range(100)],
        'low': [99.5 + i * 0.1 for i in range(100)],
        'close': [100.2 + i * 0.1 for i in range(100)],
        'volume': [1000 + i * 10 for i in range(100)]
    }
    df = pd.DataFrame(data)
    
    # Save to CSV with the symbol name
    csv_file = data_dir / "CL_5min_sample.csv"
    df.to_csv(csv_file, index=False)
    
    return data_dir


@pytest.fixture
def csv_price_time_config():
    """Create a test configuration for CSV price feed provider."""
    return PricefeedTimeframeConfig(
        supported_timeframes={
            CustomTimeframe("1m"),
            CustomTimeframe("5m"),
            CustomTimeframe("15m"),
            CustomTimeframe("30m"),
            CustomTimeframe("1h"),
            CustomTimeframe("4h"),
            CustomTimeframe("1d"),
        },
        native_timeframe=CustomTimeframe("1m"),
        resample_strategy=ResampleStrategy(
            open="first",
            high="max",
            low="min",
            close="last",
            volume="sum"
        )
    )


@pytest.fixture
def csv_config(temp_data_dir):
    """Create a test configuration for CSV price feed provider."""
    return CSVPriceFeedConfig(
        name="csv",
        data_dir=str(temp_data_dir),
        timeframes=PricefeedTimeframeConfig(
            supported_timeframes={
                CustomTimeframe("1m"),
                CustomTimeframe("5m"),
                CustomTimeframe("15m"),
                CustomTimeframe("30m"),
                CustomTimeframe("1h"),
                CustomTimeframe("4h"),
                CustomTimeframe("1d"),
            },
            native_timeframe=CustomTimeframe("1m"),
            resample_strategy=ResampleStrategy(
                open="first",
                high="max",
                low="min",
                close="last",
                volume="sum"
            ),
        ),
    )


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


def test_csv_price_time_config(csv_price_time_config):
    """Test that PricefeedTimeframeConfig can be created with custom objects."""
    conf = csv_price_time_config
    
    # Test that the configuration was created successfully
    assert len(conf.supported_timeframes) == 7
    assert conf.native_timeframe == CustomTimeframe("1m")
    assert conf.resample_strategy.open == "first"
    assert conf.resample_strategy.high == "max"
    assert conf.resample_strategy.low == "min"
    assert conf.resample_strategy.close == "last"
    assert conf.resample_strategy.volume == "sum"
    
    # Test that all expected timeframes are present
    expected_timeframes = {
        CustomTimeframe("1m"),
        CustomTimeframe("5m"),
        CustomTimeframe("15m"),
        CustomTimeframe("30m"),
        CustomTimeframe("1h"),
        CustomTimeframe("4h"),
        CustomTimeframe("1d"),
    }
    
    for tf in expected_timeframes:
        assert tf in conf.supported_timeframes


def test_csv_provider_initialization(csv_config):
    """Test CSV price feed provider initialization."""
    provider = CSVPriceFeedProvider(csv_config)
    
    assert provider.name == "csv"
    assert provider.capabilities.requires_auth is False
    assert provider.capabilities.auth_type is None
    assert len(provider.capabilities.supported_timeframes) == 7
    assert CustomTimeframe("1m") in provider.capabilities.supported_timeframes
    assert CustomTimeframe("1d") in provider.capabilities.supported_timeframes


def test_csv_provider_load_symbols(csv_config):
    """Test loading supported symbols from CSV files."""
    provider = CSVPriceFeedProvider(csv_config)
    
    # Check if test data symbols are loaded
    assert "CL_5min_sample" in provider.capabilities.supported_symbols


def test_csv_provider_get_price_data(csv_config):
    """Test fetching price data from CSV files."""
    provider = CSVPriceFeedProvider(csv_config)
    
    # Test with valid symbol and timeframe
    df = provider.get_price_data(
        symbol="CL_5min_sample",
        timeframe=CustomTimeframe("5m")
    )
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])


def test_csv_provider_invalid_symbol(csv_config):
    """Test that invalid symbols raise SymbolError."""
    provider = CSVPriceFeedProvider(csv_config)
    
    with pytest.raises(SymbolError):
        provider.get_price_data(
            symbol="INVALID",
            timeframe=CustomTimeframe("5m")
        )


def test_csv_provider_unsupported_timeframe(csv_config):
    """Test that unsupported timeframes raise TimeframeError."""
    provider = CSVPriceFeedProvider(csv_config)
    
    with pytest.raises(TimeframeError):
        provider.get_price_data(
            symbol="CL_5min_sample",
            timeframe=CustomTimeframe("2h")
        )


def test_csv_provider_resample_data(csv_config):
    """Test resampling price data to different timeframes."""
    provider = CSVPriceFeedProvider(csv_config)
    
    # Get 1-minute data
    df_1m = provider.get_price_data(
        symbol="CL_5min_sample",
        timeframe=CustomTimeframe("1m")
    )
    
    # Get 5-minute data
    df_5m = provider.get_price_data(
        symbol="CL_5min_sample",
        timeframe=CustomTimeframe("5m")
    )
    
    # Verify resampling
    assert len(df_5m) <= len(df_1m)
    # Note: We can't check freq directly since we're not setting it in the resampled data


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
    
    # Test with invalid symbol
    mock_ticker_instance.info = None
    with pytest.raises(SymbolError):
        provider.get_price_data(
            symbol="INVALID",
            timeframe=CustomTimeframe("1d")
        )
    
    # Test with unsupported timeframe
    with pytest.raises(TimeframeError):
        provider.get_price_data(
            symbol="AAPL",
            timeframe=CustomTimeframe("1h")
        )


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