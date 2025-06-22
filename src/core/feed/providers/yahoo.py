"""Yahoo Finance price feed provider."""

from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf

from src.core.time import CustomTimeframe

from ...protocols import AuthType, PriceFeedCapabilities, SymbolError, TimeframeError
from ..config import YahooFinanceConfig


class YahooFinanceProvider:
    """Yahoo Finance price feed provider."""
    
    def __init__(self, config: YahooFinanceConfig):
        """Initialize the Yahoo Finance provider."""
        self._config = config
        self._supported_symbols = set()
        if config.api_key:
            yf.set_api_key(config.api_key)
    
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
            rate_limits=self._config.rate_limits,
            requires_auth=bool(self._config.api_key),
            auth_type=AuthType.API_KEY if self._config.api_key else None,
        )
    
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
        if timeframe not in self._config.timeframes.supported_timeframes:
            raise TimeframeError(f"Timeframe {timeframe} not supported")
        
        # Get data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        
        # Check if symbol is valid
        info = ticker.info
        if not info or 'regularMarketPrice' not in info:
            raise SymbolError(f"Symbol {symbol} not found or invalid")
        
        # Get historical data
        df = ticker.history(
            start=start_time,
            end=end_time,
            interval=timeframe.to_pandas_offset(),
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
        
        return df
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is supported by this provider."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return bool(info and 'regularMarketPrice' in info)
        except:
            return False 