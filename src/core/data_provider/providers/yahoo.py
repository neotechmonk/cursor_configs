"""Yahoo Finance price feed provider."""

from datetime import datetime
from typing import Optional, Union

import pandas as pd
import yfinance as yf
from pydantic import BaseModel, ConfigDict, field_validator

from core.data_provider.config import PricefeedTimeframeConfig
from core.data_provider.error import SymbolError, TimeframeError
from core.time import CustomTimeframe


class RawYahooFinanceConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    name: Optional[str] = None  # assigned post instantiation as its the name of the yaml file
    timeframes: dict
    api_key: Optional[str] = None
    cache_duration: str = "1h"


class YahooFinanceConfig(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    name: str
    timeframes: Union[PricefeedTimeframeConfig, dict]
    api_key: Optional[str] = None
    cache_duration: str = "1h"
    
    @field_validator('timeframes', mode='before')
    @classmethod
    def validate_timeframes(cls, v):
        if isinstance(v, dict):
            return PricefeedTimeframeConfig(**v)
        return v


class YahooFinanceProvider:
    """Yahoo Finance price feed provider."""
    
    def __init__(self, config: YahooFinanceConfig):
        """Initialize the Yahoo Finance provider."""
        self._config = config
        self._supported_symbols = set()
        # Note: yfinance doesn't have set_api_key method, API key is not used
    
    @property
    def name(self) -> str:
        """Get the provider name."""
        return self._config.name
    
    @property
    def timeframes(self) -> set[CustomTimeframe]:
        """Get the supported timeframes (both supported and native)."""
        timeframes = set(self._config.timeframes.supported_timeframes)
        timeframes.add(self._config.timeframes.native_timeframe)
        return timeframes

    @property 
    def symbols(self) -> set[str]:
        """Get the supported symbols."""
        return self._supported_symbols

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
        # Validate timeframe
        if timeframe not in self.timeframes:
            raise TimeframeError(f"Timeframe {timeframe} not supported")
        
        # Get data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        
        # Check if symbol is valid
        info = ticker.info
        if not info or 'regularMarketPrice' not in info:
            raise SymbolError(f"Symbol {symbol} not found or invalid")
        
        # Get historical data
        # Convert timeframe to yfinance format (lowercase)
        yf_interval = str(timeframe).lower()
        df = ticker.history(
            start=start_time,
            end=end_time,
            interval=yf_interval,
        )
        
        if df.empty:
            raise SymbolError(f"No data available for symbol {symbol}")
        
        # Reset index to get timestamp as column
        df = df.reset_index()
        df = df.rename(columns={'Date': 'timestamp'})
        
        # Normalize column names to lowercase
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Ensure timestamp column exists (in case Date was already the index)
        if 'timestamp' not in df.columns and 'Date' in df.columns:
            df = df.rename(columns={'Date': 'timestamp'})
        
        return df
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is supported by this provider."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return bool(info and 'regularMarketPrice' in info)
        except Exception:
            return False


