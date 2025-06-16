"""Protocols (interfaces) for the trading system components."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Set, Union

import pandas as pd
from pydantic_core import CoreSchema, core_schema
from pydantic_core.core_schema import ValidationInfo


class TimeframeUnit(Enum):
    """Units of time for custom timeframes."""
    MINUTE = ("minute", 1)
    HOUR = ("hour", 60)
    DAY = ("day", 24 * 60)
    WEEK = ("week", 7 * 24 * 60)
    MONTH = ("month", 30 * 24 * 60)  # Using 30 days as average month length
    YEAR = ("year", 365 * 24 * 60)   # Using 365 days as standard year length

    def __init__(self, label: str, minutes: int):
        self.label = label
        self.minutes = minutes

    def __str__(self) -> str:
        return self.label

    @property
    def minutes_per_unit(self) -> int:
        """Get the number of minutes in one unit of this timeframe."""
        return self.minutes


class CustomTimeframe:
    """Custom timeframe implementation."""
    
    def __init__(self, value: int, unit: TimeframeUnit):
        """Initialize a custom timeframe.
        
        Args:
            value: The number of units
            unit: The unit of time
        """
        self.value = value
        self.unit = unit
    
    def __str__(self) -> str:
        """Get string representation of timeframe."""
        return f"{self.value}{self.unit.label[0]}"
    
    def __eq__(self, other: object) -> bool:
        """Check if two timeframes are equal."""
        if not isinstance(other, CustomTimeframe):
            return False
        return self.value == other.value and self.unit == other.unit
    
    def __hash__(self) -> int:
        """Get hash value for timeframe."""
        return hash((self.value, self.unit))
    
    @property
    def minutes(self) -> int:
        """Get the number of minutes in this timeframe."""
        return self.value * self.unit.minutes_per_unit
    
    def to_pandas_offset(self) -> str:
        """Convert to pandas offset string.
        
        Returns:
            String representation of the timeframe for pandas
        """
        if self.unit == TimeframeUnit.MINUTE:
            return f"{self.value}min"
        elif self.unit == TimeframeUnit.HOUR:
            return f"{self.value}H"
        elif self.unit == TimeframeUnit.DAY:
            return f"{self.value}D"
        elif self.unit == TimeframeUnit.WEEK:
            return f"{self.value}W"
        return "1min"  # Default to 1 minute
    
    @classmethod
    def from_string(cls, timeframe_str: str) -> "CustomTimeframe":
        """Create a CustomTimeframe from a string representation.
        
        Args:
            timeframe_str: String in format "1m", "5m", "1h", "4h", "1d", "1w"
            
        Returns:
            CustomTimeframe instance
            
        Raises:
            ValueError: If the string format is invalid
        """
        if not timeframe_str:
            raise ValueError("Timeframe string cannot be empty")
        
        # Extract number and unit
        number = ""
        unit = ""
        for char in timeframe_str:
            if char.isdigit():
                number += char
            else:
                unit += char
        
        if not number or not unit:
            raise ValueError(f"Invalid timeframe format: {timeframe_str}")
        
        value = int(number)
        
        # Map short unit codes to TimeframeUnit values
        unit_map = {
            "m": TimeframeUnit.MINUTE,
            "h": TimeframeUnit.HOUR,
            "d": TimeframeUnit.DAY,
            "w": TimeframeUnit.WEEK
        }
        
        if unit not in unit_map:
            raise ValueError(f"Invalid timeframe unit: {unit}")
        
        return cls(value, unit_map[unit])
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> CoreSchema:
        """Get Pydantic core schema for CustomTimeframe.
        
        This method allows Pydantic to validate and serialize CustomTimeframe objects.
        """
        def validate_timeframe(value: Union[str, Dict[str, Any]], info: ValidationInfo) -> "CustomTimeframe":
            if isinstance(value, str):
                return cls.from_string(value)
            elif isinstance(value, dict):
                if "value" not in value or "unit" not in value:
                    raise ValueError("Invalid timeframe dictionary format")
                try:
                    unit = TimeframeUnit(value["unit"], 0)
                except ValueError:
                    raise ValueError(f"Invalid timeframe unit: {value['unit']}")
                return cls(value["value"], unit)
            elif isinstance(value, CustomTimeframe):
                return value
            raise ValueError(f"Invalid timeframe value: {value}")
        
        return core_schema.json_or_python_schema(
            json_schema=core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.dict_schema(
                    core_schema.str_schema(),
                    core_schema.any_schema(),
                ),
            ]),
            python_schema=core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.dict_schema(
                    core_schema.str_schema(),
                    core_schema.any_schema(),
                ),
                core_schema.is_instance_schema(CustomTimeframe),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: {"value": x.value, "unit": x.unit.label},
                return_schema=core_schema.dict_schema(
                    core_schema.str_schema(),
                    core_schema.any_schema(),
                ),
                when_used="json",
            ),
        )


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
    supported_timeframes: Set[CustomTimeframe]
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
    timeframe: CustomTimeframe
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