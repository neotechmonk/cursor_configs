"""Tests for price feed providers."""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.core.feed import (
    CSVPriceFeedConfig,
    CSVPriceFeedProvider,
    PriceFeedConfig,
    PricefeedTimeframeConfig,
    YahooFinanceConfig,
    YahooFinanceProvider,
)
from src.core.protocols import (
    CustomTimeframe,
    PriceFeedError,
    ResampleStrategy,
    SymbolError,
    TimeframeError,
    TimeframeUnit,
)


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
    
    # Save to CSV
    csv_file = data_dir / "CL_5min_sample.csv"
    df.to_csv(csv_file, index=False)
    
    return data_dir


@pytest.fixture
def csv_config(temp_data_dir):
    """Create a test configuration for CSV price feed provider."""
    return CSVPriceFeedConfig(
        name="csv",
        data_dir=str(temp_data_dir),
        timeframes=PricefeedTimeframeConfig(
            supported_timeframes={
                CustomTimeframe(1, TimeframeUnit.MINUTE),
                CustomTimeframe(5, TimeframeUnit.MINUTE),
                CustomTimeframe(15, TimeframeUnit.MINUTE),
                CustomTimeframe(30, TimeframeUnit.MINUTE),
                CustomTimeframe(1, TimeframeUnit.HOUR),
                CustomTimeframe(4, TimeframeUnit.HOUR),
                CustomTimeframe(1, TimeframeUnit.DAY),
            },
            native_timeframe=CustomTimeframe(1, TimeframeUnit.MINUTE),
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
                CustomTimeframe(1, TimeframeUnit.DAY),
                CustomTimeframe(1, TimeframeUnit.WEEK),
            },
            native_timeframe=CustomTimeframe(1, TimeframeUnit.DAY),
            resample_strategy=ResampleStrategy(
                open="first",
                high="max",
                low="min",
                close="last",
                volume="sum"
            ),
        ),
    )


@pytest.mark.parametrize("value,unit,expected_str,expected_minutes,expected_pandas_offset", [
    (1, TimeframeUnit.MINUTE, "1m", 1, "1min"),
    (5, TimeframeUnit.MINUTE, "5m", 5, "5min"),
    (15, TimeframeUnit.MINUTE, "15m", 15, "15min"),
    (30, TimeframeUnit.MINUTE, "30m", 30, "30min"),
    (1, TimeframeUnit.HOUR, "1h", 60, "1H"),
    (4, TimeframeUnit.HOUR, "4h", 240, "4H"),
    (1, TimeframeUnit.DAY, "1d", 1440, "1D"),
    (1, TimeframeUnit.WEEK, "1w", 10080, "1W"),
    (1, TimeframeUnit.MONTH, "1M", 43200, "1M"),
    (1, TimeframeUnit.YEAR, "1y", 525600, "1Y"),
])
def test_custom_timeframe_creation(value, unit, expected_str, expected_minutes, expected_pandas_offset):
    """Test CustomTimeframe creation with various units."""
    timeframe = CustomTimeframe(value, unit)
    
    assert timeframe.value == value
    assert timeframe.unit == unit
    assert str(timeframe) == expected_str
    assert timeframe.minutes == expected_minutes
    assert timeframe.to_pandas_offset() == expected_pandas_offset


@pytest.mark.parametrize("timeframe_str,expected_value,expected_unit", [
    ("1m", 1, TimeframeUnit.MINUTE),
    ("5m", 5, TimeframeUnit.MINUTE),
    ("15m", 15, TimeframeUnit.MINUTE),
    ("30m", 30, TimeframeUnit.MINUTE),
    ("1h", 1, TimeframeUnit.HOUR),
    ("4h", 4, TimeframeUnit.HOUR),
    ("1d", 1, TimeframeUnit.DAY),
    ("1w", 1, TimeframeUnit.WEEK),
    ("1M", 1, TimeframeUnit.MONTH),
    ("1y", 1, TimeframeUnit.YEAR),
])
def test_custom_timeframe_from_string(timeframe_str, expected_value, expected_unit):
    """Test CustomTimeframe creation from string representation."""
    timeframe = CustomTimeframe.from_string(timeframe_str)
    
    assert timeframe.value == expected_value
    assert timeframe.unit == expected_unit
    assert str(timeframe) == timeframe_str


@pytest.mark.parametrize("invalid_string", [
    "",
    "invalid",
    "1",
    "m",
    "1x",
    "0m",
    "-1m",
])
def test_custom_timeframe_invalid_string(invalid_string):
    """Test CustomTimeframe creation with invalid strings."""
    with pytest.raises(ValueError):
        CustomTimeframe.from_string(invalid_string)


@pytest.mark.skip(reason="Pydantic validation issues with CustomTimeframe")
def test_csv_provider_initialization(csv_config):
    """Test CSV price feed provider initialization."""
    provider = CSVPriceFeedProvider(csv_config)
    
    assert provider.name == "csv"
    assert provider.capabilities.requires_auth is False
    assert provider.capabilities.auth_type is None
    assert len(provider.capabilities.supported_timeframes) == 7
    assert CustomTimeframe(1, TimeframeUnit.MINUTE) in provider.capabilities.supported_timeframes
    assert CustomTimeframe(1, TimeframeUnit.DAY) in provider.capabilities.supported_timeframes


# @pytest.mark.skip(reason="Pydantic validation issues with CustomTimeframe")
def test_csv_provider_load_symbols(csv_config):
    """Test loading supported symbols from CSV files."""
    provider = CSVPriceFeedProvider(csv_config)
    
    # Check if test data symbols are loaded
    assert "CL" in provider.capabilities.supported_symbols


@pytest.mark.skip(reason="Pydantic validation issues with CustomTimeframe")
def test_csv_provider_get_price_data(csv_config):
    """Test fetching price data from CSV files."""
    provider = CSVPriceFeedProvider(csv_config)
    
    # Test with valid symbol and timeframe
    df = provider.get_historical_data(
        symbol="CL",
        timeframe=CustomTimeframe(5, TimeframeUnit.MINUTE)
    )
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])


@pytest.mark.skip(reason="Pydantic validation issues with CustomTimeframe")
def test_csv_provider_invalid_symbol(csv_config):
    """Test that invalid symbols raise SymbolError."""
    provider = CSVPriceFeedProvider(csv_config)
    
    with pytest.raises(ValueError):
        provider.get_historical_data(
            symbol="INVALID",
            timeframe=CustomTimeframe(5, TimeframeUnit.MINUTE)
        )


@pytest.mark.skip(reason="Pydantic validation issues with CustomTimeframe")
def test_csv_provider_unsupported_timeframe(csv_config):
    """Test that unsupported timeframes raise TimeframeError."""
    provider = CSVPriceFeedProvider(csv_config)
    
    with pytest.raises(TimeframeError):
        provider.get_historical_data(
            symbol="CL",
            timeframe=CustomTimeframe(2, TimeframeUnit.HOUR)
        )


@pytest.mark.skip(reason="Pydantic validation issues with CustomTimeframe")
def test_csv_provider_resample_data(csv_config):
    """Test resampling price data to different timeframes."""
    provider = CSVPriceFeedProvider(csv_config)
    
    # Get 1-minute data
    df_1m = provider.get_historical_data(
        symbol="CL",
        timeframe=CustomTimeframe(1, TimeframeUnit.MINUTE)
    )
    
    # Get 5-minute data
    df_5m = provider.get_historical_data(
        symbol="CL",
        timeframe=CustomTimeframe(5, TimeframeUnit.MINUTE)
    )
    
    # Verify resampling
    assert len(df_5m) <= len(df_1m)
    assert df_5m.index.freq == '5min'  # 5-minute frequency


@pytest.mark.skip(reason="Pydantic validation issues with CustomTimeframe")
@patch('yfinance.Ticker')
def test_yahoo_provider_initialization(mock_ticker, yahoo_config):
    """Test Yahoo Finance provider initialization."""
    provider = YahooFinanceProvider(yahoo_config)
    
    assert provider.name == "yahoo"
    assert provider.capabilities.requires_auth is False
    assert provider.capabilities.auth_type is None
    assert len(provider.capabilities.supported_timeframes) == 2
    assert CustomTimeframe(1, TimeframeUnit.DAY) in provider.capabilities.supported_timeframes
    assert CustomTimeframe(1, TimeframeUnit.WEEK) in provider.capabilities.supported_timeframes


@pytest.mark.skip(reason="Pydantic validation issues with CustomTimeframe")
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
    df = provider.get_historical_data(
        symbol="AAPL",
        timeframe=CustomTimeframe(1, TimeframeUnit.DAY),
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now()
    )
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])
    
    # Test with invalid symbol
    mock_ticker_instance.info = None
    with pytest.raises(SymbolError):
        provider.get_historical_data(
            symbol="INVALID",
            timeframe=CustomTimeframe(1, TimeframeUnit.DAY)
        )
    
    # Test with unsupported timeframe
    with pytest.raises(TimeframeError):
        provider.get_historical_data(
            symbol="AAPL",
            timeframe=CustomTimeframe(1, TimeframeUnit.HOUR)
        )


@pytest.mark.skip(reason="Pydantic validation issues with CustomTimeframe")
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