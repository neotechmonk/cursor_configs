#!/usr/bin/env python3

import tempfile

from core.feed.providers.csv_file import CSVPriceFeedConfig, CSVPriceFeedProvider
from src.core.time import CustomTimeframe

# Create a temporary directory
temp_dir = tempfile.mkdtemp()
print(f"Created temp dir: {temp_dir}")

# Create the config
config = CSVPriceFeedConfig(
    name="csv",
    timeframes={
        "supported_timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        "native_timeframe": "1m",
        "resample_strategy": {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        }
    },
    data_dir=temp_dir,
    file_pattern="*.csv",
    date_format="%Y-%m-%d %H:%M:%S"
)

print(f"Config timeframes type: {type(config.timeframes)}")
print(f"Config timeframes: {config.timeframes}")
print(f"Supported timeframes: {config.timeframes.supported_timeframes}")
print(f"Supported timeframes type: {type(config.timeframes.supported_timeframes)}")

# Test the timeframe we're looking for
tf = CustomTimeframe("5m")
print(f"\nLooking for: {tf}, type: {type(tf)}")
print(f"5m in supported_timeframes: {tf in config.timeframes.supported_timeframes}")

# Create provider
provider = CSVPriceFeedProvider(config)
print(f"\nProvider timeframes: {provider.timeframes}")
print(f"Provider timeframes type: {type(provider.timeframes)}")
print(f"5m in provider.timeframes: {tf in provider.timeframes}")

# Test each timeframe individually
for timeframe in provider.timeframes:
    print(f"  {timeframe} (type: {type(timeframe)}) == {tf}: {timeframe == tf}")

# Clean up
import shutil

shutil.rmtree(temp_dir) 
