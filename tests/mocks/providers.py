from dataclasses import dataclass

import pandas as pd

from core.data_provider.protocol import DataProviderProtocol
from core.execution_provider.protocol import ExecutionProviderProtocol


@dataclass
class MockIBExecutionProvider(ExecutionProviderProtocol):
    name: str = "ib"
    
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        print(f"Submitting order for {symbol} on {timeframe} with {order_type} type, quantity {quantity} at {price}")
        return pd.DataFrame({
            'order_id': ['mock_ib_123'],
            'status': ['executed'],
            'symbol': [symbol],
            'quantity': [quantity],
            'price': [price]
        })


@dataclass
class MockAlpacaExecutionProvider(ExecutionProviderProtocol):
    name: str = "alpaca"
    
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        print(f"Submitting order for {symbol} on {timeframe} with {order_type} type, quantity {quantity} at {price}")
        return pd.DataFrame({
            'order_id': ['mock_alpaca_123'],
            'status': ['executed'],
            'symbol': [symbol],
            'quantity': [quantity],
            'price': [price]
        })


class MockExecutionProviderService:
    def __init__(self):
        self._providers = {
            "ib": MockIBExecutionProvider(),
            "alpaca": MockAlpacaExecutionProvider(),
        }
    
    def get(self, key):
        return self._providers.get(key)


@dataclass
class MockCSVDataProvider(DataProviderProtocol):
    """Mock CSV provider for testing."""
    name: str = "csv"
    
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        print(f"Getting price data for {symbol} on {timeframe}")
        return pd.DataFrame()


@dataclass
class DummyDataProvider(DataProviderProtocol):
    """A provider that follows the protocol but doesn't inherit."""
    name: str = "dummy" 
    
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        print(f"Getting price data for {symbol} on {timeframe}")
        return pd.DataFrame()


class MockDataProviderService:
    def __init__(self):
        self._providers = {
            "csv": MockCSVDataProvider(),
            "dummy": DummyDataProvider(),
        }
    
    def get(self, key):
        return self._providers.get(key)

