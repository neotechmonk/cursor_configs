"""Protocols (interfaces) for the trading system components."""

from decimal import Decimal
from typing import Dict, List, Protocol

import pandas as pd
from pydantic import BaseModel

from .time import CustomTimeframe


class Position(BaseModel):
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


class SymbolConfig(BaseModel):
    """Configuration for a trading symbol."""
    symbol: str
    price_feed: str  # Provider name
    timeframe: CustomTimeframe
    feed_config: Dict[str, str]  # Provider-specific configuration


class RiskConfig(BaseModel):
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