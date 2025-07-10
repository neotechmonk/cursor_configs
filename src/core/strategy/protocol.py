from typing import Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class StrategyProtocol(Protocol):
    """Protocol for price feed providers."""