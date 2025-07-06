from typing import Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class DataProvider(Protocol):
    """Protocol for price feed providers."""
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:...