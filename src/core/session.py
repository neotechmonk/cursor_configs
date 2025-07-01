"""Trading session management implementation."""

from typing import Dict, List

import pandas as pd

from core.feed.protocols import PriceFeedProvider

from .protocols import Portfolio, SymbolConfig, TradingSession


class SimpleTradingSession(TradingSession):
    """Simple trading session implementation."""
    
    def __init__(
        self,
        name: str,
        symbols: Dict[str, SymbolConfig],
        portfolio: Portfolio,
        price_feeds: Dict[str, PriceFeedProvider],
        strategies: List[str] = None
    ):
        """Initialize a new trading session."""
        self._name = name
        self._symbols = symbols
        self._portfolio = portfolio
        self._price_feeds = price_feeds
        self._strategies = strategies or []
    
    @property
    def name(self) -> str:
        """Session name."""
        return self._name
    
    @property
    def symbols(self) -> Dict[str, SymbolConfig]:
        """Trading symbols configuration."""
        return self._symbols
    
    @property
    def portfolio(self) -> Portfolio:
        """Associated portfolio."""
        return self._portfolio
    
    @property
    def strategies(self) -> List[str]:
        """List of strategy names in this session."""
        return self._strategies
    
    def get_price_data(self, symbol: str) -> pd.DataFrame:
        """Get price data for a symbol."""
        if symbol not in self._symbols:
            raise ValueError(f"Symbol {symbol} not configured in session {self._name}")
        
        config = self._symbols[symbol]
        if config.price_feed not in self._price_feeds:
            raise ValueError(
                f"Price feed {config.price_feed} not available for symbol {symbol}"
            )
        
        provider = self._price_feeds[config.price_feed]
        
        # Get the provider's method signature to filter feed_config
        import inspect
        method_sig = inspect.signature(provider.get_price_data)
        valid_params = set(method_sig.parameters.keys()) - {'self'}
        
        # Filter feed_config to only include valid parameters
        filtered_config = {
            k: v for k, v in config.feed_config.items() 
            if k in valid_params
        }
        
        return provider.get_price_data(
            symbol=symbol,
            timeframe=config.timeframe,
            **filtered_config
        ) 