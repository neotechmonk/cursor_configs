"""Advanced loader for trading system configuration using Pydantic v2 features."""

from datetime import datetime, timedelta
from typing import Dict, Protocol, runtime_checkable

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator

# Test data moved to test fixtures - see tests/core/loaders/test_trading_session_loader.py

# Simple Dummy provider for testing
class DummyPriceFeedProvider:
    """Dummy price feed provider for testing."""
    
    def __init__(self, name: str = "dummy"):
        self.name = name
    
    def get_price_data(self, symbol: str, timeframe: str, **kwargs) -> pd.DataFrame:
        """Generate dummy price data."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=10)
        dates = pd.date_range(start=start_time, end=end_time, periods=100)
        
        base_price = 100.0
        data = {
            'timestamp': dates,
            'open': [base_price + i * 0.1 for i in range(100)],
            'high': [base_price + 0.5 + i * 0.1 for i in range(100)],
            'low': [base_price - 0.5 + i * 0.1 for i in range(100)],
            'close': [base_price + 0.2 + i * 0.1 for i in range(100)],
            'volume': [1000 + i * 10 for i in range(100)]
        }
        return pd.DataFrame(data)


class RiskLimits(BaseModel):
    """Risk management configuration."""
    model_config = ConfigDict(frozen=True)
    
    max_position_size: float
    max_drawdown: float
    stop_loss_pct: float
    take_profit_pct: float


@runtime_checkable
class PriceFeedProtocol(Protocol):
    """Protocol for price feed providers."""
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        ...


class SymbolConfigModel(BaseModel):
    """Symbol configuration model."""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    symbol: str
    price_feed: PriceFeedProtocol
    timeframe: str
    
    @field_validator('price_feed', mode='before')
    @classmethod
    def validate_price_feed(cls, v, info):
        """Convert string to provider using container registry."""
        if isinstance(v, str):
            context = info.context or {}
            providers = context.get('providers')
            
            if providers:
                return providers[v]
            
            raise Exception("Provider not found")
        
        # If it's already an object, just return it (for duck typing)
        return v


class PortfolioConfig(BaseModel):
    """Portfolio configuration."""
    model_config = ConfigDict(frozen=True)
    
    name: str
    initial_capital: float
    risk_limits: RiskLimits


class TradingSessionConfig(BaseModel):
    """Trading session configuration."""
    model_config = ConfigDict(frozen=True, extra="ignore", arbitrary_types_allowed=True)
    
    name: str
    symbols: Dict[str, SymbolConfigModel]
    portfolio: str

# Test functions moved to test files - see tests/core/loaders/test_trading_session_loader.py


