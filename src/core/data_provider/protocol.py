from typing import Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class DataProviderProtocol(Protocol):
    """Protocol for price feed providers."""
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:...


class DataProviderServiceProtocol(Protocol):
    def get(self, name: str) -> DataProviderProtocol:...
    def get_all(self) -> list[DataProviderProtocol]:...
