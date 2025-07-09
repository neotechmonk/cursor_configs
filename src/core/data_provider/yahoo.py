# """Yahoo Finance price feed provider."""

# from datetime import datetime
# from typing import Dict, Optional

# import pandas as pd
# import yfinance as yf
# from pydantic import ConfigDict

# from core.data_provider.error import SymbolError, TimeframeError
# from core.feed.config import PricefeedTimeframeConfig
# from core.time import CustomTimeframe


# class YahooFinanceConfig():
#     """Yahoo Finance specific configuration."""
#     model_config = ConfigDict(
#         validate_assignment=True,
#         extra='forbid'
#     )
    
#     name: Optional[str] = None
#     timeframes: PricefeedTimeframeConfig
#     api_key: str | None = None
#     cache_duration: str = "1h"
#     rate_limits: Dict[str, int] 


# class YahooFinanceProvider:
#     """Yahoo Finance price feed provider."""
    
#     def __init__(self, config: YahooFinanceConfig):
#         """Initialize the Yahoo Finance provider."""
#         self._config = config
#         self._supported_symbols = set()
#         if config.api_key:
#             yf.set_api_key(config.api_key)
    
#     @property
#     def name(self) -> str:
#         """Get the provider name."""
#         return self._config.name
    
#     def get_price_data(
#         self,
#         symbol: str,
#         timeframe: CustomTimeframe,
#         start_time: Optional[datetime] = None,
#         end_time: Optional[datetime] = None,
#     ) -> pd.DataFrame:
#         """Get price data for a symbol and timeframe.
        
#         Args:
#             symbol: Symbol to get data for
#             timeframe: Timeframe for the data
#             start_time: Start time for the data
#             end_time: End time for the data
            
#         Returns:
#             DataFrame with price data
            
#         Raises:
#             SymbolError: If symbol is not supported
#             TimeframeError: If timeframe is not supported
#         """
#         # Validate timeframe
#         if timeframe not in self._config.timeframes.supported_timeframes:
#             raise TimeframeError(f"Timeframe {timeframe} not supported")
        
#         # Get data from Yahoo Finance
#         ticker = yf.Ticker(symbol)
        
#         # Check if symbol is valid
#         info = ticker.info
#         if not info or 'regularMarketPrice' not in info:
#             raise SymbolError(f"Symbol {symbol} not found or invalid")
        
#         # Get historical data
#         df = ticker.history(
#             start=start_time,
#             end=end_time,
#             interval=timeframe.to_pandas_offset(),
#         )
        
#         if df.empty:
#             raise SymbolError(f"No data available for symbol {symbol}")
        
#         # Reset index to get timestamp as column
#         df = df.reset_index()
#         df = df.rename(columns={'Date': 'timestamp'})
        
#         # Normalize column names to lowercase
#         df = df.rename(columns={
#             'Open': 'open',
#             'High': 'high', 
#             'Low': 'low',
#             'Close': 'close',
#             'Volume': 'volume'
#         })
        
#         return df
    
#     def validate_symbol(self, symbol: str) -> bool:
#         """Check if a symbol is supported by this provider."""
#         try:
#             ticker = yf.Ticker(symbol)
#             info = ticker.info
#             return bool(info and 'regularMarketPrice' in info)
#         except Exception:
#             return False


