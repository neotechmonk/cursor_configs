"""Price feed providers for the trading system."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Set

import pandas as pd
import yfinance as yf

from .config import PriceFeedConfig, PriceFeedConfigLoader, ResampleStrategy
from .protocols import (
    AuthError,
    AuthType,
    CustomTimeframe,
    PriceFeedCapabilities,
    PriceFeedError,
    PriceFeedProvider,
    RateLimitError,
    SymbolError,
    TimeframeError,
)


class YahooFinanceProvider:
    """Yahoo Finance price feed provider."""
    
    def __init__(self):
        self._capabilities = PriceFeedCapabilities(
            supported_timeframes={
                Timeframe.D1,  # Daily
                Timeframe.W1,  # Weekly
            },
            supported_symbols=set(),  # Dynamic based on validation
            rate_limits={
                "requests_per_minute": 60,
                "requests_per_day": 2000,
            },
            auth_type=None,  # No auth required
        )
    
    @property
    def name(self) -> str:
        return "yahoo_finance"
    
    @property
    def capabilities(self) -> PriceFeedCapabilities:
        return self._capabilities
    
    def get_price_data(
        self,
        symbol: str,
        timeframe: Timeframe,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Fetch price data from Yahoo Finance.
        
        Args:
            symbol: The trading symbol to fetch data for
            timeframe: The timeframe for the price data
            start_time: Optional start time for the data range
            end_time: Optional end time for the data range
            
        Returns:
            DataFrame containing the price data
            
        Raises:
            SymbolError: If the symbol is invalid or not supported
            TimeframeError: If the timeframe is not supported
        """
        # Validate timeframe
        if timeframe not in self.capabilities.supported_timeframes:
            raise TimeframeError(
                f"Timeframe {timeframe.value} not supported by {self.name}"
            )
        
        # Validate symbol
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if not info:
                raise SymbolError(f"Invalid symbol: {symbol}")
        except Exception as e:
            raise SymbolError(f"Error validating symbol {symbol}: {str(e)}")
        
        # Set default time range if not provided
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(days=365)  # Default to 1 year
        
        # Map timeframe to Yahoo Finance interval
        interval_map = {
            Timeframe.D1: "1d",
            Timeframe.W1: "1wk",
        }
        
        # Fetch data
        try:
            df = ticker.history(
                start=start_time,
                end=end_time,
                interval=interval_map[timeframe]
            )
            
            if df.empty:
                raise SymbolError(f"No data available for symbol: {symbol}")
                
            return df
            
        except Exception as e:
            raise SymbolError(f"Error fetching data for {symbol}: {str(e)}")

    def _to_yahoo_interval(self, timeframe: CustomTimeframe) -> str:
        """Convert CustomTimeframe to Yahoo Finance interval string.
        
        Args:
            timeframe: The timeframe to convert
            
        Returns:
            Yahoo Finance interval string
            
        Raises:
            TimeframeError: If the timeframe cannot be converted
        """
        # Map timeframe to Yahoo Finance interval
        interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
            "1w": "1wk"
        }
        
        interval = interval_map.get(str(timeframe))
        if not interval:
            raise TimeframeError(f"Unsupported timeframe for Yahoo Finance: {timeframe}")
            
        return interval


class CSVPriceFeedProvider(PriceFeedProvider):
    """Price feed provider that reads data from CSV files."""
    
    def __init__(self, config: PriceFeedConfig):
        """Initialize the CSV price feed provider.
        
        Args:
            config: Configuration for the price feed provider
        """
        self._config = config
        self._data_dir = Path(config.data_dir)
        self._supported_symbols: Set[str] = set()
        self._load_supported_symbols()
    
    @property
    def name(self) -> str:
        """Get the provider name."""
        return "csv"
    
    @property
    def capabilities(self) -> PriceFeedCapabilities:
        """Get the provider's capabilities."""
        return PriceFeedCapabilities(
            supported_timeframes=self._config.timeframes.supported_timeframes,
            supported_symbols=self._supported_symbols,
            rate_limits={},  # No rate limits for CSV files
            requires_auth=False,
            auth_type=None,
        )
    
    def _load_supported_symbols(self) -> None:
        """Load the list of supported symbols from the data directory."""
        if not self._data_dir.exists():
            raise PriceFeedError(f"Data directory not found: {self._data_dir}")
        
        # Look for CSV files in the data directory
        for file in self._data_dir.glob("*.csv"):
            # Extract symbol from filename (e.g., "BTCUSDT.csv" -> "BTCUSDT")
            symbol = file.stem
            self._supported_symbols.add(symbol)
    
    def get_price_data(
        self,
        symbol: str,
        timeframe: CustomTimeframe,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Fetch price data for a given symbol and timeframe.
        
        Args:
            symbol: The trading symbol to fetch data for
            timeframe: The timeframe for the price data
            start_time: Optional start time for the data range
            end_time: Optional end time for the data range
            
        Returns:
            DataFrame containing the price data
            
        Raises:
            SymbolError: If the symbol is invalid or not supported
            TimeframeError: If the timeframe is not supported
        """
        # Validate symbol
        if not self.validate_symbol(symbol):
            raise SymbolError(f"Symbol not supported: {symbol}")
        
        # Validate timeframe
        if timeframe not in self._config.timeframes.supported_timeframes:
            raise TimeframeError(f"Timeframe not supported: {timeframe}")
        
        # Load data from CSV file
        file_path = self._data_dir / f"{symbol}.csv"
        if not file_path.exists():
            raise SymbolError(f"Data file not found for symbol: {symbol}")
        
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Convert timestamp column to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Filter by time range if specified
        if start_time:
            df = df[df.index >= start_time]
        if end_time:
            df = df[df.index <= end_time]
        
        # If timeframe is not the native timeframe, resample the data
        if timeframe != self._config.timeframes.native_timeframe:
            df = self._resample_data(df, timeframe)
        
        return df
    
    def _resample_data(self, df: pd.DataFrame, timeframe: CustomTimeframe) -> pd.DataFrame:
        """Resample price data to the requested timeframe.
        
        Args:
            df: DataFrame with price data at native timeframe
            timeframe: Target timeframe for resampling
            
        Returns:
            Resampled DataFrame
        """
        # Get resample strategy
        strategy = self._config.timeframes.resample_strategy
        
        # Create resampled DataFrame
        resampled = pd.DataFrame()
        
        # Apply resampling rules
        if 'open' in df.columns:
            resampled['open'] = df['open'].resample(timeframe.to_pandas_offset()).first()
        if 'high' in df.columns:
            resampled['high'] = df['high'].resample(timeframe.to_pandas_offset()).max()
        if 'low' in df.columns:
            resampled['low'] = df['low'].resample(timeframe.to_pandas_offset()).min()
        if 'close' in df.columns:
            resampled['close'] = df['close'].resample(timeframe.to_pandas_offset()).last()
        if 'volume' in df.columns:
            resampled['volume'] = df['volume'].resample(timeframe.to_pandas_offset()).sum()
        
        return resampled
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is supported by this provider.
        
        Args:
            symbol: The symbol to validate
            
        Returns:
            True if the symbol is supported, False otherwise
        """
        return symbol in self._supported_symbols 