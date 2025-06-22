"""Loader for trading system configuration."""

from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel

from core.portfolio import SimplePortfolio
from core.price_feeds import YahooFinanceProvider
from core.protocols import SymbolConfig, Timeframe
from core.session import SimpleTradingSession


class PriceFeedConfig(BaseModel):
    """Price feed configuration."""
    provider: str
    config: Dict[str, str | List[str]]  # Allow both string and list of strings


class RiskLimits(BaseModel):
    """Risk management configuration."""
    max_position_size: float
    max_drawdown: float
    stop_loss_pct: float
    take_profit_pct: float


class PortfolioConfig(BaseModel):
    """Portfolio configuration."""
    name: str
    initial_capital: float
    risk_limits: RiskLimits


class SymbolConfigModel(BaseModel):
    """Symbol configuration model."""
    symbol: str
    price_feed: str
    timeframe: str
    feed_config: Dict[str, str]


class TradingSessionConfig(BaseModel):
    """Trading session configuration."""
    name: str
    symbols: Dict[str, SymbolConfigModel]
    portfolio: str
    price_feeds: list[str]


class TradingConfig(BaseModel):
    """Complete trading system configuration."""
    price_feeds: Dict[str, PriceFeedConfig]
    portfolio: PortfolioConfig
    trading_sessions: Dict[str, TradingSessionConfig]


class TradingConfigLoader:
    """Loader for trading system configuration."""
    
    def __init__(self, config_path: Path):
        """Initialize the loader."""
        self.config_path = config_path
        self.config: Optional[TradingConfig] = None
    
    def load(self) -> TradingConfig:
        """Load the configuration from file."""
        with open(self.config_path) as f:
            config_dict = yaml.safe_load(f)
        self.config = TradingConfig.model_validate(config_dict)
        return self.config
    
    def create_price_feeds(self) -> Dict[str, YahooFinanceProvider]:
        """Create price feed providers from configuration."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        feeds = {}
        for name, feed_config in self.config.price_feeds.items():
            if feed_config.provider == "yahoo":
                feeds[name] = YahooFinanceProvider(feed_config.config)
            else:
                raise ValueError(f"Unsupported price feed provider: {feed_config.provider}")
        return feeds
    
    def create_portfolio(self) -> SimplePortfolio:
        """Create portfolio from configuration."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        return SimplePortfolio(
            name=self.config.portfolio.name,
            initial_capital=self.config.portfolio.initial_capital,
            risk_limits=self.config.portfolio.risk_limits.model_dump()
        )
    
    def create_trading_sessions(
        self,
        price_feeds: Dict[str, YahooFinanceProvider],
        portfolio: SimplePortfolio
    ) -> Dict[str, SimpleTradingSession]:
        """Create trading sessions from configuration."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        sessions = {}
        for name, session_config in self.config.trading_sessions.items():
            # Convert symbol configs
            symbols = {}
            for symbol_name, symbol_config in session_config.symbols.items():
                symbols[symbol_name] = SymbolConfig(
                    symbol=symbol_config.symbol,
                    price_feed=symbol_config.price_feed,
                    timeframe=Timeframe(symbol_config.timeframe),
                    feed_config=symbol_config.feed_config
                )
            
            # Create session
            sessions[name] = SimpleTradingSession(
                name=session_config.name,
                symbols=symbols,
                portfolio=portfolio,
                price_feeds={name: price_feeds[name] for name in session_config.price_feeds}
            )
        return sessions 