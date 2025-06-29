"""Protocols for price feed providers."""

from datetime import datetime
from enum import Enum
from typing import Optional, Protocol

import pandas as pd
from pydantic import BaseModel

from ..time import CustomTimeframe


class PriceFeedProvider(Protocol):
    """Protocol for price feed providers."""
    
    def get_price_data(
        self,
        symbol: str,
        timeframe: CustomTimeframe,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Fetch price data for a given symbol and timeframe.
        
        This method handles all necessary validation including:
        - Symbol validity
        - Provider readiness
        - Rate limits
        - Authentication status
        
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
            RateLimitError: If rate limits are exceeded
            AuthError: If authentication is required but not provided
        """
        ...


class AuthType(Enum):
    """Authentication types for price feed providers."""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    # Add other auth types as needed


#FIX: move this to provider specific resampling for now and later make generic if needed
class ResampleStrategy(BaseModel):
    """Strategy for resampling price data.
    
    Attributes:
        open: Aggregation method for open prices (e.g., "first")
        high: Aggregation method for high prices (e.g., "max")
        low: Aggregation method for low prices (e.g., "min")
        close: Aggregation method for close prices (e.g., "last")
        volume: Aggregation method for volume (e.g., "sum")
    """
    open: str
    high: str
    low: str
    close: str
    volume: str