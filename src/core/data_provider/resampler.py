from typing import Protocol

import pandas as pd
from pydantic import BaseModel
from typing_extensions import deprecated

from core.time import CustomTimeframe


class ResamplerProtocol(Protocol):
    def __call__(self, data: pd.DataFrame, from_timeframe: CustomTimeframe, to_timeframe: CustomTimeframe) -> pd.DataFrame:
        ...


def pandas_resampler(
        data: pd.DataFrame,
        from_timeframe: CustomTimeframe,
        to_timeframe: CustomTimeframe,
    ) -> pd.DataFrame:
        return data.resample(to_timeframe.to_pandas_offset()).agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        })


@deprecated("Use PandasResampler instead")
class ResampleStrategy(BaseModel):    
    """Strategy for resampling price data.
    
    Attributes:
        open: Aggregation method for open prices (e.g., "first")
        high: Aggregation method for high prices (e.g., "max")
        low: Aggregation method for low prices (e.g., "min")
        close: Aggregation method for close prices (e.g., "last")
        volume: Aggregation method for volume (e.g., "sum")
    """
    open: str
    high: str
    low: str
    close: str
    volume: str