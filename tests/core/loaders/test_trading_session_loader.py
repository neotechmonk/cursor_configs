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
    TypeVar,
    Union,
    overload,
    runtime_checkable,
)
from unittest.mock import Mock

import pandas as pd
import pytest
from dependency_injector import containers, providers
from pydantic import BaseModel, ConfigDict, field_validator

from core.container.provider import PriceFeedsContainer
from core.sessions.protocols import TradingSessionProtocol

"""
TODO   : 
1. [x] Lock in the yaml format for the trading session
2. [ ] Seperate Portfolio out of this
3. [ ] Utility function / pattern to validate str nested models vs obect nested models
4. [ ] Can Trading session loader  itself be called by a container? whats the value compared to doing in manually
5. [ ] Portfolio needs to be loaded from context like Symbol Condif
6. [ ] What if DI calls are made to lazily load providers/strategies/etc?


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
    "symbols": {
        "CL": {
            "symbol": "CL",
                "providers": {
                    "data": "csv",
                    "execution": "ib"
                },
            "timeframe": "5m",
                "enabled": True,
        }, 
        "AAPL": {
            "symbol": "AAPL",
                "providers": {
                    "data": "dummy",
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
            "csv": MockCSVDataProvider(),
            "dummy": DummyDataProvider()
        },
        "providers.execution": {
            "ib": MockIBExecutionProvider(),
            "alpaca": MockAlpacaExecutionProvider()
        }
    }
# Test data is now centralized in the trading_session_data fixture above

# Protocol definition







    

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
    

    
    

@pytest.fixture
def container_context() -> TradingSessionProtocol:
    """Fixture for provider context."""
    providers = {
        "data": {
            "csv": MockCSVDataProvider(),
            "dummy": DummyDataProvider()
        },
        "execution": {
            "ib": MockIBExecutionProvider(),
            "alpaca": MockAlpacaExecutionProvider()
        }
    }
    
    class Container:
        def get(self, *, key: str, type: Literal['data', 'execution']) -> Union[DataProvider, ExecutionProvider]:
            return providers[type][key]
    
    return Container()

# Domain-specific container protocols
class DataProviderServiceProtocol(Protocol):
    """Protocol for data provider services."""
    def get(self, name: str) -> DataProvider:
        """Get data provider by name.
        implements ServiceProtocol.get()
        """
        ...
    
    def get_all(self) -> list[DataProvider]:
        """Get all data providers.
        implements ServiceProtocol.get_all()
        """
        ...

class ExecutionProviderServiceProtocol(Protocol):
    """Protocol for execution provider services."""
    def get(self, name: str) -> ExecutionProvider:
        """Get execution provider by name.
        implements ServiceProtocol.get()
        """
        ...
    
    def get_all(self) -> list[ExecutionProvider]:
        """Get all execution providers.
        implements ServiceProtocol.get_all()
        """
        ...

class StrategyServiceProtocol(Protocol):
    """Protocol for strategy services."""
    def get(self, name: str) -> Any:  # Strategy type
        """Get strategy by name.
        implements ServiceProtocol.get()
        """
        ...
    
    def get_all(self) -> list[Any]:  # Strategy type
        """Get all strategies.
        implements ServiceProtocol.get_all()
        """
        ...

        ...

class TradingSessionCoordinatingContainer(containers.DeclarativeContainer):
    """Coordinating container using dependency_injector framework."""
    
    # Configuration
    config = providers.Configuration()
    
    # Dependencies - inject domain containers
    data_provider_container = providers.Dependency(ServiceProtocol, default=PriceFeedsContainer)
    execution_provider_container = providers.Dependency(ServiceProtocol)
    strategy_container = providers.Dependency(StrategyServiceProtocol, default=None)
    portfolio_container = providers.Dependency(PortfolioServiceProtocol, default=None)
    
    # Provider factory methods - consistent with provided checks
    def get_data_provider(self, *, name: str) -> DataProvider:
        """Get data provider by name - coordinates with data provider container."""
        if self.data_provider_container.provided:
            return self.data_provider_container().get(name)
        else:
            raise ValueError("Data provider container not provided")
        
    def get_execution_provider(self, *, name: str) -> ExecutionProvider:
        """Get execution provider by name - coordinates with execution provider container."""
        if self.execution_provider_container.provided:
            return self.execution_provider_container().get(name)
        else:
            raise ValueError("Execution provider container not provided")
    
    def get_strategy(self, *, name: str) -> Any:
        """Get strategy by name - coordinates with strategy container."""
        if self.strategy_container.provided:
            return self.strategy_container().get(name)
        else:
            raise ValueError("Strategy container not provided")
    
    def get_portfolio(self, *, name: str) -> Any:
        """Get portfolio by name - coordinates with portfolio container."""
        if self.portfolio_container.provided:
            return self.portfolio_container().get(name)
        else:
            raise ValueError("Portfolio container not provided")
    
    # Validation methods - consistent with provided checks
    def validate_data_provider_exists(self, *, name: str) -> bool:
        """Validate that a data provider exists without loading it."""
        if not self.data_provider_container.provided:
            return False
        try:
            self.data_provider_container().get(name)
            return True
        except (KeyError, ValueError):
            return False
    
    def validate_execution_provider_exists(self, *, name: str) -> bool:
        """Validate that an execution provider exists without loading it."""
        if not self.execution_provider_container.provided:
            return False
        try:
            self.execution_provider_container().get(name)
            return True
        except (KeyError, ValueError):
            return False
    
    def validate_strategy_exists(self, *, name: str) -> bool:
        """Validate that a strategy exists without loading it."""
        if not self.strategy_container.provided:
            return False
        try:
            self.strategy_container().get(name)
            return True
        except (KeyError, ValueError):
            return False
    
    def validate_portfolio_exists(self, *, name: str) -> bool:
        """Validate that a portfolio exists without loading it."""
        if not self.portfolio_container.provided:
            return False
        try:
            self.portfolio_container().get(name)
            return True
        except (KeyError, ValueError):
            return False
    
    # Unified provider method for backward compatibility
    def get_provider(self, *, key: str, type: Literal['data', 'execution']) -> Union[DataProvider, ExecutionProvider]:
        """Get provider by type and name - unified API for validation."""
        if type == "data":
            return self.get_data_provider(name=key)
        elif type == "execution":
            return self.get_execution_provider(name=key)
        else:
            raise ValueError(f"Invalid provider type: {type}")
    
    def wire(self, *args, **kwargs) -> None:
        """Wire the container and validate dependencies."""
        super().wire(*args, **kwargs)
        
        # Validate that required containers are provided
        if not self.data_provider_container.provided:
            raise ValueError("data_provider_container is required but not provided")
        if not self.execution_provider_container.provided:
            raise ValueError("execution_provider_container is required but not provided")

# Domain containers using DI framework
class TestDataProviderContainer(containers.DeclarativeContainer):
    """Test data provider container using dependency_injector."""
    
    # Configuration
    config = providers.Configuration()
    
    # Provider instances
    csv_provider = providers.Singleton(MockCSVDataProvider)
    dummy_provider = providers.Singleton(DummyDataProvider)
    
    # Factory method
    def get(self, name: str) -> DataProvider:
        """Get data provider by name."""
        providers_map = {
            "csv": self.csv_provider,
            "dummy": self.dummy_provider
        }
        if name not in providers_map:
            raise ValueError(f"Data provider '{name}' not found")
        return providers_map[name]()

class TestExecutionProviderContainer(containers.DeclarativeContainer):
    """Test execution provider container using dependency_injector."""
    
    # Configuration
    config = providers.Configuration()
    
    # Provider instances
    ib_provider = providers.Singleton(MockIBExecutionProvider)
    alpaca_provider = providers.Singleton(MockAlpacaExecutionProvider)
    
    # Factory method
    def get(self, name: str) -> ExecutionProvider:
        """Get execution provider by name."""
        providers_map = {
            "ib": self.ib_provider,
            "alpaca": self.alpaca_provider
        }
        if name not in providers_map:
            raise ValueError(f"Execution provider '{name}' not found")
        return providers_map[name]()

class TestStrategyContainer(containers.DeclarativeContainer):
    """Test strategy container using dependency_injector."""
    
    # Configuration
    config = providers.Configuration()
    
    # Strategy instances
    trend_following_strategy = providers.Singleton(lambda: Mock(spec=Strategy))
    mean_reversion_strategy = providers.Singleton(lambda: Mock(spec=Strategy))
    
    # Factory method
    def get_strategy(self, name: str) -> Any:
        """Get strategy by name."""
        strategies_map = {
            "trend_following": self.trend_following_strategy,
            "mean_reversion": self.mean_reversion_strategy
        }
        if name not in strategies_map:
            raise ValueError(f"Strategy '{name}' not found")
        return strategies_map[name]()

class TestPortfolioContainer(containers.DeclarativeContainer):
    """Test portfolio container using dependency_injector."""
    
    # Configuration
    config = providers.Configuration()
    
    # Portfolio instances
    main_portfolio = providers.Singleton(lambda: Mock(spec=Portfolio))
    
    # Factory method
    def get_portfolio(self, name: str) -> Any:
        """Get portfolio by name."""
        portfolios_map = {
            "Main Portfolio": self.main_portfolio
        }
        if name not in portfolios_map:
            raise ValueError(f"Portfolio '{name}' not found")
        return portfolios_map[name]()

# Updated fixture that creates DI-based coordinating container
@pytest.fixture
def coordinating_container() -> TradingSessionCoordinatingContainer:
    """Fixture for coordinating container using dependency_injector."""
    
    # Create domain containers
    data_provider_container = TestDataProviderContainer()
    execution_provider_container = TestExecutionProviderContainer()
    strategy_container = TestStrategyContainer()
    portfolio_container = TestPortfolioContainer()
    
    # Wire domain containers
    data_provider_container.wire()
    execution_provider_container.wire()
    strategy_container.wire()
    portfolio_container.wire()
    
    # Create coordinating container with dependencies
    coordinating_container = TradingSessionCoordinatingContainer()
    coordinating_container.data_provider_container.override(data_provider_container)
    coordinating_container.execution_provider_container.override(execution_provider_container)
    coordinating_container.strategy_container.override(strategy_container)
    coordinating_container.portfolio_container.override(portfolio_container)
    
    # Wire coordinating container
    coordinating_container.wire()
    
    return coordinating_container

# Updated SymbolConfigModelV2 to use DI-based coordinating container
class SymbolConfigModelV2(BaseModel):
    """Symbol configuration model with DI-based coordinating container."""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    symbol: str
    providers: dict[Literal['data', 'execution'], Union[DataProvider, ExecutionProvider]]
    timeframe: str
    enabled: bool
    
    @field_validator('providers', mode='before')
    @classmethod
    def validate_provider(cls, v, info):
        """Convert string provider names to actual provider instances using DI-based coordinating container."""
        if isinstance(v, dict):
            context = info.context or {}
            container = context.get('container')
            
            if container and isinstance(container, TradingSessionCoordinatingContainer):
                for provider_type, provider_name in v.items():
                    if isinstance(provider_name, str):
                        # Use DI-based coordinating container's unified API
                        provider = container.get_provider(key=provider_name, type=provider_type)
                        if provider is None:
                            raise ValueError(f"{provider_type.title()} provider '{provider_name}' not found")
                        v[provider_type] = provider
            else:
                # Fallback to old approach
                for provider_type, provider_name in v.items():
                    if isinstance(provider_name, str):
                        providers = context.get(f"providers.{provider_type}", {})
                        provider = next((p for p in providers.values() 
                                       if getattr(p, 'name', None) == provider_name), None)
                        if provider is None:
                            raise ValueError(f"{provider_type.title()} provider '{provider_name}' not found")
                        v[provider_type] = provider
        
        return v

# Updated tests to use DI-based coordinating container
def test_di_coordinating_container_validation(coordinating_container):
    """Test that DI-based coordinating container properly validates providers."""
    
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
    
    config = SymbolConfigModelV2.model_validate(
        symbol_data,
        context={'container': coordinating_container}
    )
    
    assert config.symbol == "CL"
    assert config.timeframe == "5m"
    assert config.enabled 
    assert "data" in config.providers
    assert "execution" in config.providers
    assert isinstance(config.providers["data"], MockCSVDataProvider)
    assert isinstance(config.providers["execution"], MockIBExecutionProvider)

# Test coordinating container validation methods
def test_coordinating_container_validation_methods(coordinating_container):
    """Test the validation methods of the coordinating container."""
    
    # Test provider validation
    assert coordinating_container.validate_data_provider_exists(name="csv") == True
    assert coordinating_container.validate_execution_provider_exists(name="ib") == True
    assert coordinating_container.validate_data_provider_exists(name="invalid") == False
    
    # Test strategy validation
    assert coordinating_container.validate_strategy_exists(name="trend_following") == True
    assert coordinating_container.validate_strategy_exists(name="invalid") == False
    
    # Test portfolio validation
    assert coordinating_container.validate_portfolio_exists(name="Main Portfolio") == True
    assert coordinating_container.validate_portfolio_exists(name="invalid") == False

# Test coordinating container with missing dependencies
def test_coordinating_container_missing_dependencies():
    """Test coordinating container behavior when dependencies are missing."""
    
    # Create minimal container without optional dependencies
    coordinating_container = TradingSessionCoordinatingContainer()
    
    # Create required containers
    data_provider_container = TestDataProviderContainer()
    execution_provider_container = TestExecutionProviderContainer()
    
    # Wire required containers
    data_provider_container.wire()
    execution_provider_container.wire()
    
    # Override only required dependencies
    coordinating_container.data_provider_container.override(data_provider_container)
    coordinating_container.execution_provider_container.override(execution_provider_container)
    
    # Wire coordinating container
    coordinating_container.wire()
    
    # Provider methods should work
    assert coordinating_container.get_data_provider(name="csv") is not None
    assert coordinating_container.get_execution_provider(name="ib") is not None
    
    # Strategy methods should raise error
    with pytest.raises(ValueError, match="Strategy container not provided"):
        coordinating_container.get_strategy(name="trend_following")
    
    # Portfolio methods should raise error
    with pytest.raises(ValueError, match="Portfolio container not provided"):
        coordinating_container.get_portfolio(name="Main Portfolio")

if __name__ == "__main__":
    # Run tests
    # test_price_feed_protocol_validation()
    # test_string_to_provider_conversion()
    # test_duck_typing_direct_object()
    # test_trading_session_with_multiple_symbols()
    # test_error_handling_invalid_provider()
    
    print("✅ All tests passed!")