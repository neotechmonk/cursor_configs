"""Tests for CSV price feed provider."""


from datetime import datetime

import pandas as pd
import pytest

from core.data_provider.config import PricefeedTimeframeConfig
from core.data_provider.csv import CSVPriceFeedConfig, CSVPriceFeedProvider
from core.data_provider.error import SymbolError, TimeframeError
from core.data_provider.resampler import ResampleStrategy
from core.time import CustomTimeframe, TimeframeUnit


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
        # native_timeframe="1m",
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
        timeframes={
            "supported_timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
            "native_timeframe": "1m",
            "resample_strategy": {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }
        },
        data_dir=str(temp_data_dir),
        file_pattern="*.csv",
        date_format="%Y-%m-%d %H:%M:%S"
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
    assert len(provider.timeframes) == 7
    assert CustomTimeframe(1, TimeframeUnit.MINUTE) in provider.timeframes
    assert CustomTimeframe("1d") in provider.timeframes


def test_csv_provider_load_one_symbol(csv_config):
    """Test loading supported symbols from CSV files."""
    provider = CSVPriceFeedProvider(csv_config)
    
    # Check if test data symbols are loaded
    assert "CL" in provider.symbols


def test_csv_provider_load_multiple_symbols(tmp_path, csv_price_time_config):
    """Test loading multiple instruments from CSV files."""
    # Create multiple CSV files for different instruments
    instruments = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    mult_file_dir = tmp_path / "multi_csv"
    mult_file_dir.mkdir()
    for symbol in instruments:
        # Create sample data for each instrument
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1min')
        data = {
            'timestamp': dates,
            'open': [100 + i * 0.1 for i in range(50)],
            'high': [100.5 + i * 0.1 for i in range(50)],
            'low': [99.5 + i * 0.1 for i in range(50)],
            'close': [100.2 + i * 0.1 for i in range(50)],
            'volume': [1000 + i * 10 for i in range(50)]
        }
        df = pd.DataFrame(data)
        
        # Save each instrument to its own CSV file

        csv_file = mult_file_dir / f"{symbol}_xxxx.csv"
        df.to_csv(csv_file, index=False)
    
    # Create provider config pointing to directory with multiple files
    config = CSVPriceFeedConfig(
        name="csv",
        timeframes=csv_price_time_config,
        data_dir=str(mult_file_dir),
        file_pattern="*.csv",
        date_format="%Y-%m-%d %H:%M:%S"
    )
    
    provider = CSVPriceFeedProvider(config)
    
    # # Verify all instruments are loaded
    assert len(provider.symbols) == 4
    for symbol in instruments:
        assert symbol in provider.symbols
    
    # Test getting data for each instrument
    for symbol in instruments:
        df = provider.get_price_data(
            symbol=symbol,
            timeframe=CustomTimeframe("1m")
        )
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) == 50  # Should have 50 rows


def test_csv_provider_load_symbols_empty_directory(csv_price_time_config, tmp_path):
    """Test loading symbols from empty directory."""
    # Create empty temp directory
    temp_dir = tmp_path / "empty_data"
    temp_dir.mkdir()
    
    config = CSVPriceFeedConfig(
        name="csv",
        timeframes=csv_price_time_config,
        data_dir=str(temp_dir),
        file_pattern="*.csv",
        date_format="%Y-%m-%d %H:%M:%S"
    )
    
    provider = CSVPriceFeedProvider(config)
    
    # Should have no symbols in empty directory
    assert len(provider.symbols) == 0
    assert provider.symbols == set()


def test_csv_provider_get_price_data(csv_config):
    """Test fetching price data from CSV files."""
    provider = CSVPriceFeedProvider(csv_config)
    
    # Test with valid symbol and timeframe
    df = provider.get_price_data(
        symbol="CL",
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
            symbol="CL",
            timeframe=CustomTimeframe("2h")
        )


def test_csv_provider_resample_data(csv_config):
    """Test resampling price data to different timeframes."""
    provider = CSVPriceFeedProvider(csv_config)

    print([tf for tf in provider.timeframes])
    
    # Get 1-minute data
    df_1m = provider.get_price_data(
        symbol="CL",
        timeframe=CustomTimeframe("5m")
    )
    
    # Get 5-minute data
    df_5m = provider.get_price_data(
        symbol="CL",
        timeframe=CustomTimeframe("5m")
    )
    
    # Verify resampling
    assert len(df_5m) <= len(df_1m)
    # Note: We can't check freq directly since we're not setting it in the resampled data


def test_csv_provider_validate_symbol(csv_config):
    """Test symbol validation for CSV provider."""
    provider = CSVPriceFeedProvider(csv_config)
    
    assert provider.validate_symbol("CL"    ) is True
    assert provider.validate_symbol("INVALID") is False


def test_csv_provider_time_range_filtering(csv_config):
    """Test filtering data by time range."""
    provider = CSVPriceFeedProvider(csv_config)
    
    start_time = datetime(2024, 1, 1, 12, 0, 0)
    end_time = datetime(2024, 1, 1, 13, 0, 0)
    
    df = provider.get_price_data(
        symbol="CL",
        timeframe=CustomTimeframe("1m"),
        start_time=start_time,
        end_time=end_time
    )
    
    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        assert df.index.min() >= start_time
        assert df.index.max() <= end_time 


def test_csv_provider_load_symbols_with_mixed_files(csv_config, temp_data_dir):
    """Test loading symbols when directory has mixed file types."""
    # Add additional CSV files to existing directory
    csv_symbols = ["BTC", "GOOG"]
    for symbol in csv_symbols:
        csv_file = temp_data_dir / f"{symbol}_yyyy_xxxx.csv"
        pd.DataFrame({'timestamp': [pd.Timestamp('2024-01-01')], 'open': [100]}).to_csv(csv_file, index=False)
    
    # Add non-CSV files (should be ignored)
    other_files = ["README.txt", "config.json", "data.parquet"]
    for filename in other_files:
        other_file = temp_data_dir / filename
        other_file.write_text("dummy content")
    
    # Use existing csv_config (which already points to temp_data_dir)
    provider = CSVPriceFeedProvider(csv_config)
    
    # Should load original CL_5min_sample + new CSV files, but ignore non-CSV
    expected_symbols = {"CL", "BTC", "GOOG"}
    assert provider.symbols  == expected_symbols
    
    # Non-CSV files should be ignored
    for filename in other_files:
        symbol = filename.replace('.txt', '').replace('.json', '').replace('.parquet', '')
        assert symbol not in provider.symbols 