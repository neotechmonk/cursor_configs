"""Feed configuration models."""

from typing import Dict, Optional, Set

from pydantic import BaseModel, ConfigDict

from ..time import CustomTimeframe
from .protocols import ResampleStrategy


class PricefeedTimeframeConfig(BaseModel):
    """Configuration for timeframes."""
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    supported_timeframes: Set[CustomTimeframe] 
    native_timeframe: CustomTimeframe 
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

