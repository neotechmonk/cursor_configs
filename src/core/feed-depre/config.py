"""Feed configuration models."""

from typing import Annotated, Set

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




