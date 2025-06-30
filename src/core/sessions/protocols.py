"""Protocols for trading sessions."""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Protocol

import pandas as pd


class TradingSession(Protocol):
    """Protocol for trading sessions."""
    
    @property
    def name(self) -> str:
        """Session name."""
        ...
    
    @property
    def portfolio_name(self) -> str:
        """Associated portfolio name."""
        ...
    
    @property
    def capital_allocation(self) -> Decimal:
        """Allocated capital for this session."""
        ...
    
    @property
    def strategies(self) -> List[str]:
        """List of strategy names in this session."""
        ...
    
    def get_symbol_config(self, symbol: str) -> Dict[str, Any]:
        """Get configuration for a symbol.
        
        Args:
            symbol: Symbol to get config for
            
        Returns:
            Symbol configuration including data_provider, execution_provider, timeframe
            
        Raises:
            ValueError: If symbol not found in session
        """
        ...
    
    def get_price_data(self, symbol: str) -> pd.DataFrame:
        """Get price data for a symbol.
        
        Args:
            symbol: Symbol to get data for
            
        Returns:
            Price data DataFrame
            
        Raises:
            ValueError: If symbol not found or data provider unavailable
        """
        ...
    
    def get_session_pnl(self) -> Decimal:
        """Get current session P&L.
        
        Returns:
            Session P&L as decimal
        """
        ...
    
    def get_allocated_capital(self) -> Decimal:
        """Get allocated capital for this session.
        
        Returns:
            Allocated capital amount
        """
        ...
    
    def is_symbol_enabled(self, symbol: str) -> bool:
        """Check if a symbol is enabled in this session.
        
        Args:
            symbol: Symbol to check
            
        Returns:
            True if symbol is enabled, False otherwise
        """
        ...
    
    def get_enabled_symbols(self) -> List[str]:
        """Get list of enabled symbols in this session.
        
        Returns:
            List of enabled symbol names
        """
        ...