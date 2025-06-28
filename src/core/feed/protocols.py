"""Protocols for price feed providers."""

from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Protocol, Set

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


class PriceFeedError(Exception):
    """Base class for price feed errors."""
    pass


class SymbolError(PriceFeedError):
    """Error raised when a symbol is invalid or not supported."""
    pass


class TimeframeError(PriceFeedError):
    """Error raised when a timeframe is not supported."""
    pass


class RateLimitError(PriceFeedError):
    """Error raised when rate limits are exceeded."""
    pass


class AuthError(PriceFeedError):
    """Error raised when authentication fails."""
    pass


class PriceFeedCapabilities(BaseModel):
    """Capabilities and limitations of a price feed provider."""
    supported_timeframes: Set[CustomTimeframe]
    supported_symbols: Set[str]
    rate_limits: Dict[str, int]  # e.g., {"requests_per_minute": 60}
    requires_auth: bool
    auth_type: Optional[AuthType]  # e.g., "api_key", "oauth2"


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