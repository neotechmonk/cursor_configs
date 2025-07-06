from dataclasses import dataclass

import pandas as pd


class MockIBExecutionProvider():
    name: str = "ib"
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        print(f"Submitting order for {symbol} on {timeframe} with {order_type} type, quantity {quantity} at {price}")


@dataclass
class MockAlpacaExecutionProvider:
    name: str = "alpaca"
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        print(f"Submitting order for {symbol} on {timeframe} with {order_type} type, quantity {quantity} at {price}")
    

@dataclass
class MockCSVDataProvider:
    """Mock CSV provider for testing."""
    name: str = "csv"
    
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        print(f"Getting price data for {symbol} on {timeframe}")
        return pd.DataFrame()


@dataclass
class DummyDataProvider:
    """A provider that follows the protocol but doesn't inherit."""
    name: str = "dummy" 
    
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        print(f"Getting price data for {symbol} on {timeframe}")
        return pd.DataFrame()
