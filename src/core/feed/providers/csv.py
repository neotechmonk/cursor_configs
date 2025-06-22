"""CSV price feed provider."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from src.core.time import CustomTimeframe

from ...protocols import PriceFeedCapabilities, SymbolError, TimeframeError
from ..config import CSVPriceFeedConfig


class CSVPriceFeedProvider:
    """CSV price feed provider."""
    
    def __init__(self, config: CSVPriceFeedConfig):
        """Initialize the CSV price feed provider."""
        self._config = config
        self._data_dir = Path(config.data_dir)
        self._supported_symbols = set()
        self._load_supported_symbols()
    
    @property
    def name(self) -> str:
        """Get the provider name."""
        return self._config.name
    
    @property
    def capabilities(self) -> PriceFeedCapabilities:
        """Get the provider's capabilities."""
        return PriceFeedCapabilities(
            supported_timeframes=self._config.timeframes.supported_timeframes,
            supported_symbols=self._supported_symbols,
            rate_limits={},
            requires_auth=False,
            auth_type=None,
        )
    
    def _load_supported_symbols(self) -> None:
        """Load supported symbols from CSV files."""
        self._supported_symbols = {
            f.stem for f in self._data_dir.glob(self._config.file_pattern)
        }
    
    def get_price_data(
        self,
        symbol: str,
        timeframe: CustomTimeframe,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Get price data for a symbol and timeframe.
        
        Args:
            symbol: Symbol to get data for
            timeframe: Timeframe for the data
            start_time: Start time for the data
            end_time: End time for the data
            
        Returns:
            DataFrame with price data
            
        Raises:
            SymbolError: If symbol is not supported
            TimeframeError: If timeframe is not supported
        """
        # Validate symbol
        if symbol not in self._supported_symbols:
            raise SymbolError(f"Symbol {symbol} not supported")
        
        # Validate timeframe
        if timeframe not in self._config.timeframes.supported_timeframes:
            raise TimeframeError(f"Timeframe {timeframe} not supported")
        
        # Load data from CSV
        file_path = self._data_dir / f"{symbol}.csv"
        if not file_path.exists():
            raise SymbolError(f"Data file for symbol {symbol} not found")
        
        df = pd.read_csv(file_path, parse_dates=["timestamp"])
        
        # Filter by date range if provided
        if start_time:
            df = df[df["timestamp"] >= start_time]
        if end_time:
            df = df[df["timestamp"] <= end_time]
        
        # Resample if needed (if timeframe is not native)
        if timeframe != self._config.timeframes.native_timeframe:
            df = self._resample_data(df, timeframe)
        
        return df
    
    def _resample_data(self, df: pd.DataFrame, timeframe: CustomTimeframe) -> pd.DataFrame:
        """Resample data to the requested timeframe."""
        # Set timestamp as index for resampling
        df = df.set_index("timestamp")
        
        # Get resample strategy
        strategy = self._config.timeframes.resample_strategy
        
        # Resample using the strategy
        resampled = df.resample(timeframe.to_pandas_offset()).agg({
            'open': strategy.open,
            'high': strategy.high,
            'low': strategy.low,
            'close': strategy.close,
            'volume': strategy.volume
        })
        
        # Reset index to get timestamp back as column
        return resampled.reset_index()
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is supported by this provider."""
        return symbol in self._supported_symbols 