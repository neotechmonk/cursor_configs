"""Feed configuration models."""

from typing import Dict, Set

from pydantic import BaseModel, ConfigDict

from src.core.protocols import ResampleStrategy
from src.core.time import CustomTimeframe


class PricefeedTimeframeConfig(BaseModel):
    """Configuration for timeframes."""
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    supported_timeframes: Set[CustomTimeframe] 
    native_timeframe: CustomTimeframe 
    resample_strategy: ResampleStrategy


class PriceFeedConfig(BaseModel):
    """Base configuration for price feed providers."""
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    name: str
    timeframes: PricefeedTimeframeConfig


class YahooFinanceConfig(PriceFeedConfig):
    """Yahoo Finance specific configuration."""
    api_key: str | None = None
    cache_duration: str = "1h"
    rate_limits: Dict[str, int]


class CSVPriceFeedConfig(PriceFeedConfig):
    """CSV price feed specific configuration."""
    data_dir: str
    file_pattern: str = "*.csv"
    date_format: str = "%Y-%m-%d %H:%M:%S" 