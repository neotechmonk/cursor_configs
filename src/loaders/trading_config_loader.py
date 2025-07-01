"""Loader for trading system configuration."""

from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel

from core.feed.providers.csv_file import CSVPriceFeedConfig, CSVPriceFeedProvider
from core.portfolio import SimplePortfolio
from core.protocols import SymbolConfig
from core.session import SimpleTradingSession
from core.time import CustomTimeframe


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
    strategies: Optional[Dict[str, dict]] = None


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
    
    def create_price_feeds(self) -> Dict[str, CSVPriceFeedProvider]:
        """Create price feed providers from configuration."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        feeds = {}
        for name, feed_config in self.config.price_feeds.items():
            if feed_config.provider == "csv":
                # Create proper CSV config with timeframes from the providers directory
                csv_config = CSVPriceFeedConfig(
                    name=feed_config.config.get("name", "csv"),
                    data_dir=feed_config.config.get("data_dir", "tests/data"),
                    file_pattern=feed_config.config.get("file_pattern", "*.csv"),
                    date_format=feed_config.config.get("date_format", "%Y-%m-%d %H:%M:%S"),
                    timeframes={
                        "supported_timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
                        "native_timeframe": "1m",
                        "resample_strategy": {
                            "open": "first",
                            "high": "max",
                            "low": "min",
                            "close": "last",
                            "volume": "sum"
                        }
                    }
                )
                feeds[name] = CSVPriceFeedProvider(csv_config)
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
        price_feeds: Dict[str, CSVPriceFeedProvider],
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
                    timeframe=CustomTimeframe(symbol_config.timeframe),
                    feed_config=symbol_config.feed_config
                )
            
            # Find strategies associated with this session
            strategies = []
            if hasattr(self.config, 'strategies'):
                for strategy_name, strategy_config in self.config.strategies.items():
                    if strategy_config.get('session') == name:
                        strategies.append(strategy_name)
            
            # Create session
            sessions[name] = SimpleTradingSession(
                name=session_config.name,
                symbols=symbols,
                portfolio=portfolio,
                price_feeds={name: price_feeds[name] for name in session_config.price_feeds},
                strategies=strategies
            )
        return sessions 