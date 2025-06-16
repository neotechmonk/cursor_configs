"""Protocols (interfaces) for the trading system components."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Protocol, Set

import pandas as pd


class Timeframe(Enum):
    """Supported timeframes for price data."""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


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


@dataclass
class PriceFeedCapabilities:
    """Capabilities and limitations of a price feed provider."""
    supported_timeframes: Set[Timeframe]
    supported_symbols: Set[str]
    rate_limits: Dict[str, int]  # e.g., {"requests_per_minute": 60}
    requires_auth: bool
    auth_type: Optional[AuthType]  # e.g., "api_key", "oauth2"


class PriceFeedProvider(Protocol):
    """Protocol for price feed providers."""
    
    @property
    def name(self) -> str:
        """Unique identifier for the provider."""
        ...
    
    @property
    def capabilities(self) -> PriceFeedCapabilities:
        """Provider's capabilities and limitations."""
        ...
    
    def get_price_data(
        self,
        symbol: str,
        timeframe: Timeframe,
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
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is supported by this provider."""
        ...


@dataclass
class Position:
    """Represents a trading position."""
    symbol: str
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal


class Portfolio(Protocol):
    """Protocol for portfolio management."""
    
    @property
    def name(self) -> str:
        """Portfolio name."""
        ...
    
    @property
    def initial_capital(self) -> Decimal:
        """Initial capital amount."""
        ...
    
    @property
    def current_capital(self) -> Decimal:
        """Current capital amount."""
        ...
    
    @property
    def positions(self) -> List[Position]:
        """List of all positions."""
        ...
    
    @property
    def positions_by_symbol(self) -> Dict[str, Position]:
        """Positions indexed by symbol."""
        ...
    
    def update_position(self, symbol: str, price: Decimal) -> None:
        """Update position with new price."""
        ...
    
    def can_open_position(
        self,
        symbol: str,
        quantity: Decimal,
        price: Decimal
    ) -> bool:
        """Check if portfolio can open a new position."""
        ...


@dataclass
class SymbolConfig:
    """Configuration for a trading symbol."""
    symbol: str
    price_feed: str  # Provider name
    timeframe: Timeframe
    feed_config: Dict[str, str]  # Provider-specific configuration


@dataclass
class RiskConfig:
    """Risk management configuration."""
    max_position_size: Decimal
    max_drawdown: Decimal
    stop_loss_pct: Decimal
    take_profit_pct: Decimal


class TradingSession(Protocol):
    """Protocol for trading sessions."""
    
    @property
    def name(self) -> str:
        """Session name."""
        ...
    
    @property
    def symbols(self) -> Dict[str, SymbolConfig]:
        """Trading symbols configuration."""
        ...
    
    @property
    def portfolio(self) -> Portfolio:
        """Associated portfolio."""
        ...
    
    def get_price_data(self, symbol: str) -> pd.DataFrame:
        """Get price data for a symbol."""
        ... 