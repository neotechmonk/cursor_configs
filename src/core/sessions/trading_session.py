"""Trading session implementation."""

from decimal import Decimal
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel

from .protocols import TradingSession


class SymbolMapping(BaseModel):
    """Symbol mapping configuration."""
    data_provider: str
    execution_provider: str
    timeframe: str
    enabled: bool = True


class ExecutionLimits(BaseModel):
    """Execution limits for the session."""
    max_open_positions: int
    max_order_size: float
    trading_hours: Dict[str, str] # FIX : need a better way to handle days and hour windows


class SessionConfig(BaseModel):
    """Session configuration."""
    name: str
    description: Optional[str] = None
    portfolio: str
    capital_allocation: float
    strategies: List[str]
    execution_limits: ExecutionLimits
    symbol_mapping: Dict[str, SymbolMapping]


class TradingSessionImpl(TradingSession):
    """Trading session implementation."""
    
    def __init__(self, config: SessionConfig, data_providers: Dict[str, Any], execution_providers: Dict[str, Any]):
        """Initialize trading session.
        
        Args:
            config: Session configuration
            data_providers: Available data providers
            execution_providers: Available execution providers
        """
        self._config = config
        self._data_providers = data_providers
        self._execution_providers = execution_providers
        self._session_pnl = Decimal('0.0')
    
    @property
    def name(self) -> str:
        """Session name."""
        return self._config.name
    
    @property
    def portfolio_name(self) -> str:
        """Associated portfolio name."""
        return self._config.portfolio
    
    @property
    def capital_allocation(self) -> Decimal:
        """Allocated capital for this session."""
        return Decimal(str(self._config.capital_allocation))
    
    @property
    def strategies(self) -> List[str]:
        """List of strategy names in this session."""
        return self._config.strategies.copy()
    
    def get_symbol_config(self, symbol: str) -> Dict[str, Any]:
        """Get configuration for a symbol."""
        if symbol not in self._config.symbol_mapping:
            raise ValueError(f"Symbol {symbol} not found in session {self.name}")
        
        mapping = self._config.symbol_mapping[symbol]
        return {
            "data_provider": mapping.data_provider,
            "execution_provider": mapping.execution_provider,
            "timeframe": mapping.timeframe,
            "enabled": mapping.enabled
        }
    
    def get_price_data(self, symbol: str) -> pd.DataFrame:
        """Get price data for a symbol."""
        if not self.is_symbol_enabled(symbol):
            raise ValueError(f"Symbol {symbol} is not enabled in session {self.name}")
        
        config = self.get_symbol_config(symbol)
        data_provider_name = config["data_provider"]
        
        if data_provider_name not in self._data_providers:
            raise ValueError(f"Data provider {data_provider_name} not available")
        
        provider = self._data_providers[data_provider_name]
        return provider.get_price_data(
            symbol=symbol,
            timeframe=config["timeframe"]
        )
    
    def get_session_pnl(self) -> Decimal:
        """Get current session P&L."""
        return self._session_pnl
    
    def get_allocated_capital(self) -> Decimal:
        """Get allocated capital for this session."""
        return self.capital_allocation
    
    def is_symbol_enabled(self, symbol: str) -> bool:
        """Check if a symbol is enabled in this session."""
        if symbol not in self._config.symbol_mapping:
            return False
        return self._config.symbol_mapping[symbol].enabled
    
    def get_enabled_symbols(self) -> List[str]:
        """Get list of enabled symbols in this session."""
        return [
            symbol for symbol, mapping in self._config.symbol_mapping.items()
            if mapping.enabled
        ]
    
    def update_session_pnl(self, pnl: Decimal) -> None:
        """Update session P&L."""
        self._session_pnl = pnl