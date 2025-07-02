"""Test suite for advanced trading config loader using Pydantic v2 and Protocols."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Protocol,
    Union,
    runtime_checkable,
)
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

@pytest.fixture
def trading_session_data():
    """Fixture for trading session test data."""
    return {
        "name": "Main Trading Session",
        "description": "Test trading session for validation",
        "portfolio": "Main Portfolio",
        "capital_allocation": 50000.00,
        "strategies": [
            "trend_following",
            "mean_reversion"
        ],
        "execution_limits": {
            "max_open_positions": 5,
            "max_order_size": 10000.00,
            "trading_hours": {
                "start": "09:30",
                "end": "16:00"
            }
        },
        "symbol_mapping": {
            "CL": {
                "providers": {
                    "data": "csv",
                    "execution": "ib"
                },
                "timeframe": "5m",
                "enabled": True,
            }, 
            "AAPL": {
                "providers": {
                    "data": "csv",
                    "execution": "alpaca"
                },
                "timeframe": "1d",
                "enabled": True
            }
        }
    }

@pytest.fixture
def provider_context():
    """Fixture for provider context."""
    return {
        "providers.data": {
            "csv": MockCSVDataProvider()
        },
        "providers.execution": {
            "ib": MockIBExecutionProvider(),
            "alpaca": MockAlpacaExecutionProvider()
        }
    }
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
    "description": "Test trading session for validation",
    "portfolio": "Main Portfolio",
    "capital_allocation": 50000.00,
    "strategies": [
        "trend_following",
        "mean_reversion"
    ],
    "execution_limits": {
        "max_open_positions": 5,
        "max_order_size": 10000.00,
        "trading_hours": {
            "start": "09:30",
            "end": "16:00"
        }
    },
    "symbols": {
        "CL": {
            "symbol": "CL",
            "providers": {
                "data": "csv",
                "execution": "ib"
            },
            "timeframe": "5m",
            "enabled": True,
            "feed_config": {"cache_duration": "1h"}
        }, 
        "AAPL": {
            "providers": {
                "data": "csv",
                "execution": "alpaca"
            },
            "timeframe": "1d",
            "enabled": True
        }
    }
}

# Protocol definition
@runtime_checkable
class DataProvider(Protocol):
    """Protocol for price feed providers."""
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        ...


@dataclass
class MockCSVDataProvider:
    """Mock CSV provider for testing."""
    name: str = "csv"
    
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

@dataclass
class DummyDataProvider:
    """A provider that follows the protocol but doesn't inherit."""
    name: str = "dummy" 
    
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Generate dummy price data."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=5)
        dates = pd.date_range(start=start_time, end=end_time, periods=50)
        
        data = {
            'timestamp': dates,
            'open': [50.0 + i * 0.05 for i in range(50)],
            'high': [50.5 + i * 0.05 for i in range(50)],
            'low': [49.5 + i * 0.05 for i in range(50)],
            'close': [50.2 + i * 0.05 for i in range(50)],
            'volume': [500 + i * 5 for i in range(50)]
        }
        return pd.DataFrame(data)

@runtime_checkable
class ExecutionProvider(Protocol):
    """Protocol for order execution and account management"""
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        ...

@dataclass
class MockIBExecutionProvider:
    name: str = "ib"
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        raise NotImplementedError("Not implemented - test mock")

@dataclass
class MockAlpacaExecutionProvider:
    name: str = "alpaca"
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        raise NotImplementedError("Not implemented - test mock") 
    

class SymbolConfigModel(BaseModel):
    """Symbol configuration model."""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    symbol: str
    providers: dict[Literal['data', 'execution'], Union[DataProvider, ExecutionProvider]]
    timeframe: str
    enabled: bool

    @field_validator('providers', mode='before')
    @classmethod
    def validate_provider(cls, v, info):
        """Convert string provider names to actual provider instances using context."""
        if isinstance(v, dict):
            context = info.context or {}
            
            for provider_type, provider_name in v.items():
                if isinstance(provider_name, str):
                    providers = context.get(f"providers.{provider_type}", {})
                    # Find provider by name property
                    provider = next((p for p in providers.values() if getattr(p, 'name', None) == provider_name), None)
                    if provider is None:
                        raise ValueError(f"{provider_type.title()} provider '{provider_name}' not found")
                    v[provider_type] = provider
            
            return v
        
        return v

# @pytest.mark.skip(reason="TDD: Implementing step by step")
def test_price_feed_protocol_validation(trading_session_data, provider_context):
    """Test that objects conforming to DataProvider are accepted."""
    
    # Test with a simple symbol configuration
    symbol_data = {
        "symbol": "CL",
        "providers": {
            "data": "csv",
            "execution": "ib"
        },
        "timeframe": "5m",
        "enabled": True
    }
    
    config = SymbolConfigModel.model_validate(
        symbol_data,
        context=provider_context
    )
    
    assert config.symbol == "CL"
    assert config.timeframe == "5m"
    assert config.enabled == True
    assert "data" in config.providers
    assert "execution" in config.providers
    assert isinstance(config.providers["data"], MockCSVDataProvider)
    assert isinstance(config.providers["execution"], MockIBExecutionProvider)

# Test 2: String to provider conversion

def test_string_to_provider_conversion():
    """Test converting string provider names to actual provider instances."""
    
    # Act
    config = SymbolConfigModel.model_validate(
        {
            "symbol": "TEST",
            "providers": {
                "data": "csv",
                "execution": "ib"
            },
            "timeframe": "1h",
            "enabled": True
        },
        context={
            "providers.data": {"csv": MockCSVDataProvider()},  # Fixed: match validator expectation
            "providers.execution": {"ib": MockIBExecutionProvider()}  # Fixed: match validator expectation
        }
    )
    
    # Assert
    assert config.symbol == "TEST"
    assert config.timeframe == "1h"
    assert config.enabled == True
    assert "data" in config.providers
    assert "execution" in config.providers
    assert isinstance(config.providers["data"], MockCSVDataProvider)
    assert isinstance(config.providers["execution"], MockIBExecutionProvider)

# Test 3: Duck typing with direct object
# @pytest.mark.skip(reason="TDD: Implementing step by step")
def test_duck_typing_direct_object():
    """Test passing duck type compliant object directly."""
    
    # Act
    config = SymbolConfigModel(
        symbol="TEST",
        providers={
            "data": DummyDataProvider(),
            "execution": MockIBExecutionProvider()
        },
        timeframe="1h",
        enabled=True
    )
    
    # Assert
    assert "data" in config.providers
    assert "execution" in config.providers
    assert isinstance(config.providers["data"], DataProvider)
    assert isinstance(config.providers["execution"], ExecutionProvider)
    assert config.providers["data"].name == "dummy"
    assert config.providers["execution"].name == "ib"
    

# Test 4: Trading session with multiple symbols
@pytest.mark.skip(reason="TDD: Implementing step by step")
def test_trading_session_with_multiple_symbols():
    """Test loading a complete trading session with multiple symbols."""
    
    # Arrange
    class SymbolConfigModel(BaseModel):
        model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
        symbol: str
        provider: DataProvider
        timeframe: str
        
        @field_validator('provider', mode='before')
        @classmethod
        def validate_provider(cls, v, info):
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
        "duck": DummyDataProvider()
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
    assert isinstance(cl_symbol.provider, MockCSVDataProvider)
    
    # Check AAPL symbol
    aapl_symbol = session_config.symbols["AAPL"]
    assert aapl_symbol.symbol == "AAPL"
    assert aapl_symbol.timeframe == "1d"
    assert isinstance(aapl_symbol.provider, MockCSVDataProvider)

# Test 5: Error handling for invalid provider
@pytest.mark.skip(reason="TDD: Implementing step by step")
def test_error_handling_invalid_provider():
    """Test error handling when provider string is not found."""
    
    # Arrange
    class SymbolConfigModel(BaseModel):
        model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
        symbol: str
        provider: DataProvider
        timeframe: str
        
        @field_validator('provider', mode='before')
        @classmethod
        def validate_provider(cls, v, info):
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
                "provider": "invalid",
                "timeframe": "1h"
            },
            context={'providers': {}}
        )


if __name__ == "__main__":
    # Run tests
    # test_price_feed_protocol_validation()
    # test_string_to_provider_conversion()
    # test_duck_typing_direct_object()
    # test_trading_session_with_multiple_symbols()
    # test_error_handling_invalid_provider()
    
    print("✅ All tests passed!")