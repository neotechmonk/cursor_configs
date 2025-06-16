"""Price feed implementations."""

from datetime import datetime, timedelta
from typing import Dict, Optional, Set

import pandas as pd
import yfinance as yf

from .protocols import (
    AuthType,
    PriceFeedCapabilities,
    PriceFeedProvider,
    SymbolError,
    Timeframe,
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