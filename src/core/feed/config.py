"""Feed configuration models."""

from typing import Annotated, Dict, Optional, Set

from pydantic import BaseModel, ConfigDict, PlainValidator

from ..time import CustomTimeframe
from .protocols import ResampleStrategy


def validate_timeframe(v) -> CustomTimeframe:
    if isinstance(v, str):
        return CustomTimeframe(v)
    return v


class PricefeedTimeframeConfig(BaseModel):
    """Configuration for timeframes."""
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    supported_timeframes:  Set[Annotated[CustomTimeframe, PlainValidator(validate_timeframe)]]
    native_timeframe: Annotated[CustomTimeframe, PlainValidator(validate_timeframe)]
    resample_strategy: ResampleStrategy


class YahooFinanceConfig():
    """Yahoo Finance specific configuration."""
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    name: Optional[str] = None
    timeframes: PricefeedTimeframeConfig
    api_key: str | None = None
    cache_duration: str = "1h"
    rate_limits: Dict[str, int]

