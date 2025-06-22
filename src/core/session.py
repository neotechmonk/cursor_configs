"""Trading session management implementation."""

from typing import Dict

import pandas as pd

from .protocols import Portfolio, PriceFeedProvider, SymbolConfig, TradingSession


class SimpleTradingSession(TradingSession):
    """Simple trading session implementation."""
    
    def __init__(
        self,
        name: str,
        symbols: Dict[str, SymbolConfig],
        portfolio: Portfolio,
        price_feeds: Dict[str, PriceFeedProvider]
    ):
        """Initialize a new trading session."""
        self._name = name
        self._symbols = symbols
        self._portfolio = portfolio
        self._price_feeds = price_feeds
    
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
        return provider.get_price_data(
            symbol=symbol,
            timeframe=config.timeframe,
            **config.feed_config
        ) 