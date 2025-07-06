from typing import Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class ExecutionProvider(Protocol):
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        ...