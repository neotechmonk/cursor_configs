"""Mock symbol configuration for testing the new list-based structure.

This module provides the MockSymbolConfig class used for testing session
functionality without requiring full dependency resolution.
"""

from typing import Optional

from core.data_provider.protocol import DataProviderProtocol
from core.execution_provider.protocol import ExecutionProviderProtocol
from core.strategy.protocol import StrategyProtocol
from core.time import CustomTimeframe
from tests.mocks.providers import MockCSVDataProvider, MockIBExecutionProvider
from tests.mocks.strategies import MockBreakoutStrategy


class MockSymbolConfig:
    """Mock symbol configuration for testing the new list-based structure.
    
    This class simulates a fully resolved SymbolConfigModel with all
    dependencies properly injected, used for testing session functionality
    without requiring full dependency resolution.
    """
    
    def __init__(
        self,
        symbol: str = "MOCK",
        data_provider: Optional[DataProviderProtocol] = None,
        execution_provider: Optional[ExecutionProviderProtocol] = None,
        timeframe: str = "5m",
        enabled: bool = True,
        strategy: Optional[StrategyProtocol] = None
    ):
        """Initialize mock symbol configuration.
        
        Args:
            symbol: Symbol identifier
            data_provider: Mock data provider instance
            execution_provider: Mock execution provider instance
            timeframe: Trading timeframe
            enabled: Whether symbol is enabled
            strategy: Mock strategy instance
        """
        self.symbol = symbol
        self.data_provider = data_provider or MockCSVDataProvider()
        self.execution_provider = execution_provider or MockIBExecutionProvider()
        self.timeframe = CustomTimeframe(timeframe)
        self.enabled = enabled
        self.strategy = strategy or MockBreakoutStrategy()
    
    def get_price_data(self, symbol: str, timeframe: str):
        """Mock method to get price data.
        
        Args:
            symbol: Symbol identifier
            timeframe: Trading timeframe
            
        Returns:
            Mock DataFrame with sample data
        """
        return self.data_provider.get_price_data(symbol, timeframe) 