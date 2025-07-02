"""Test suite for advanced trading config loader using Pydantic v2 and Protocols."""

from datetime import datetime, timedelta
from typing import Any, Dict, Protocol, runtime_checkable
from unittest.mock import Mock

import pandas as pd
import pytest
from pydantic import BaseModel, ConfigDict, field_validator

"""
TODO   : 
1. [ ] Lock in the yaml format for the trading session
2. [ ] Seperate Portfolio out of this
3. [ ] Utility function / pattern to validate str nested models vs obect nested models
4. [ ] Can Trading session loader  itself be called by a container? whats the value compared to doing in manually


# """
# # Test data
PORTFOLIO_DATA = {
    "portfolio": {
        "name": "Main Portfolio",
        "initial_capital": 100000.00,
        "risk_limits": {
            "max_position_size": 10000.00,
            "max_drawdown": 0.10,
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.04
        }
    }
}

TRADING_SESSION_DATA = {
    "name": "Main Trading Session",
    "symbols": {
        "CL": {
            "symbol": "CL",
            "price_feed": "csv",
            "timeframe": "5m",
        }, 
        "AAPL": {
            "symbol": "AAPL",
            "price_feed": "csv",
            "timeframe": "1d",
        }
    },
    "portfolio": "Main Portfolio"
}

# Protocol definition
@runtime_checkable
class PriceFeedProtocol(Protocol):
    """Protocol for price feed providers."""
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        ...

# Test providers
class MockCSVDataProvider:
    """Mock CSV provider for testing."""
    
    def __init__(self, name: str = "csv"):
        self.name = name
    
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Generate mock CSV data."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=5)
        dates = pd.date_range(start=start_time, end=end_time, periods=50)
        
        data = {
            'timestamp': dates,
            'open': [100.0 + i * 0.1 for i in range(50)],
            'high': [100.5 + i * 0.1 for i in range(50)],
            'low': [99.5 + i * 0.1 for i in range(50)],
            'close': [100.2 + i * 0.1 for i in range(50)],
            'volume': [1000 + i * 10 for i in range(50)]
        }
        return pd.DataFrame(data)

class DummyTypeProvider:
    """A provider that follows the protocol but doesn't inherit."""
    
    def __init__(self, name: str = "duck"):
        self.name = name
    
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:...

     

# Test 1: Basic Protocol validation
@pytest.mark.skip(reason="TDD: Implementing step by step")
def test_price_feed_protocol_validation():
    """Test that objects conforming to PriceFeedProtocol are accepted."""
    
    # Arrange
    class SymbolConfigModel(BaseModel):
        model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
        symbol: str
        price_feed: PriceFeedProtocol
        timeframe: str
    
    # Act & Assert
    # Should work with protocol-compliant object
    config = SymbolConfigModel(
        symbol="TEST",
        price_feed=DummyTypeProvider(),
        timeframe="1h"
    )
    
    assert config.symbol == "TEST"
    assert config.timeframe == "1h"
    assert isinstance(config.price_feed, PriceFeedProtocol)
    assert config.price_feed.name == "duck"

# Test 2: String to provider conversion
@pytest.mark.skip(reason="TDD: Implementing step by step")
def test_string_to_provider_conversion():
    """Test converting string provider names to actual provider instances."""
    
    # Arrange
    class SymbolConfigModel(BaseModel):
        model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
        symbol: str
        price_feed: PriceFeedProtocol
        timeframe: str
        
        @field_validator('price_feed', mode='before')
        @classmethod
        def validate_price_feed(cls, v, info):
            if isinstance(v, str):
                context = info.context or {}
                providers = context.get('providers', {})
                return providers.get(v)
            return v
    
    providers = {
        "csv": MockCSVDataProvider(),
        "duck": DummyTypeProvider()
    }
    
    # Act
    config = SymbolConfigModel.model_validate(
        {
            "symbol": "TEST",
            "price_feed": "csv",
            "timeframe": "1h"
        },
        context={'providers': providers}
    )
    
    # Assert
    assert isinstance(config.price_feed, MockCSVDataProvider)
    assert config.price_feed.name == "csv"

# Test 3: Duck typing with direct object
@pytest.mark.skip(reason="TDD: Implementing step by step")
def test_duck_typing_direct_object():
    """Test passing duck type compliant object directly."""
    
    # Arrange
    class SymbolConfigModel(BaseModel):
        model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
        symbol: str
        price_feed: PriceFeedProtocol
        timeframe: str
        
        @field_validator('price_feed', mode='before')
        @classmethod
        def validate_price_feed(cls, v, info):
            if isinstance(v, str):
                context = info.context or {}
                providers = context.get('providers', {})
                return providers.get(v)
            return v
    
    # Act
    config = SymbolConfigModel(
        symbol="TEST",
        price_feed=DummyTypeProvider(),
        timeframe="1h"
    )
    
    # Assert
    assert isinstance(config.price_feed, DummyTypeProvider)
    assert config.price_feed.name == "duck"
    
    # Test actual functionality
    df = config.price_feed.get_price_data("TEST", "1h")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 50
    assert "timestamp" in df.columns

# Test 4: Trading session with multiple symbols
@pytest.mark.skip(reason="TDD: Implementing step by step")
def test_trading_session_with_multiple_symbols():
    """Test loading a complete trading session with multiple symbols."""
    
    # Arrange
    class SymbolConfigModel(BaseModel):
        model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
        symbol: str
        price_feed: PriceFeedProtocol
        timeframe: str
        
        @field_validator('price_feed', mode='before')
        @classmethod
        def validate_price_feed(cls, v, info):
            if isinstance(v, str):
                context = info.context or {}
                providers = context.get('providers', {})
                return providers.get(v)
            return v
    
    class TradingSessionConfig(BaseModel):
        model_config = ConfigDict(frozen=True, extra="ignore", arbitrary_types_allowed=True)
        name: str
        symbols: Dict[str, SymbolConfigModel]
        portfolio: str
    
    providers = {
        "csv": MockCSVDataProvider(),
        "duck": DummyTypeProvider()
    }
    
    # Act
    session_config = TradingSessionConfig.model_validate(
        TRADING_SESSION_DATA,
        context={'providers': providers}
    )
    
    # Assert
    assert session_config.name == "Main Trading Session"
    assert session_config.portfolio == "Main Portfolio"
    assert len(session_config.symbols) == 2
    
    # Check CL symbol
    cl_symbol = session_config.symbols["CL"]
    assert cl_symbol.symbol == "CL"
    assert cl_symbol.timeframe == "5m"
    assert isinstance(cl_symbol.price_feed, MockCSVDataProvider)
    
    # Check AAPL symbol
    aapl_symbol = session_config.symbols["AAPL"]
    assert aapl_symbol.symbol == "AAPL"
    assert aapl_symbol.timeframe == "1d"
    assert isinstance(aapl_symbol.price_feed, MockCSVDataProvider)

# Test 5: Error handling for invalid provider
@pytest.mark.skip(reason="TDD: Implementing step by step")
def test_error_handling_invalid_provider():
    """Test error handling when provider string is not found."""
    
    # Arrange
    class SymbolConfigModel(BaseModel):
        model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
        symbol: str
        price_feed: PriceFeedProtocol
        timeframe: str
        
        @field_validator('price_feed', mode='before')
        @classmethod
        def validate_price_feed(cls, v, info):
            if isinstance(v, str):
                context = info.context or {}
                providers = context.get('providers', {})
                provider = providers.get(v)
                if not provider:
                    raise ValueError(f"Provider '{v}' not found")
                return provider
            return v
    
    # Act & Assert
    with pytest.raises(ValueError, match="Provider 'invalid' not found"):
        SymbolConfigModel.model_validate(
            {
                "symbol": "TEST",
                "price_feed": "invalid",
                "timeframe": "1h"
            },
            context={'providers': {}}
        )

if __name__ == "__main__":
    # Run tests
    test_price_feed_protocol_validation()
    test_string_to_provider_conversion()
    test_duck_typing_direct_object()
    test_trading_session_with_multiple_symbols()
    test_error_handling_invalid_provider()
    
    print("✅ All tests passed!")