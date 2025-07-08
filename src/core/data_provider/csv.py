import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator

from core.data_provider.config import PricefeedTimeframeConfig
from core.feed.error import SymbolError, TimeframeError
from core.time import CustomTimeframe


class RawCSVPriceFeedConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    name: Optional[str] = None # assigned post instantiation as its the name of the yaml file
    timeframes: dict
    data_dir: str
    file_pattern: str = "*.csv"
    date_format: str = "%Y-%m-%d %H:%M:%S"


class CSVPriceFeedConfig(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    name: str
    timeframes: Union[PricefeedTimeframeConfig, dict]
    data_dir: str
    file_pattern: str = "*.csv"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    @field_validator('timeframes', mode='before')
    @classmethod
    def validate_timeframes(cls, v):
        if isinstance(v, dict):
            return PricefeedTimeframeConfig(**v)
        return v


def resolve_csv_pricefeed_config(raw: RawCSVPriceFeedConfig) -> CSVPriceFeedConfig:
    warnings.warn("resolve_csv_pricefeed_config is deprecated. Use CSVPriceFeedConfig model validator instead.")
    return CSVPriceFeedConfig(
        name=raw.name,
        data_dir=raw.data_dir,
        file_pattern=raw.file_pattern,
        date_format=raw.date_format,
        timeframes=PricefeedTimeframeConfig(**raw.timeframes)
    )


class CSVPriceFeedProvider:
    """CSV price feed provider."""
    
    def __init__(self, config: CSVPriceFeedConfig):
        """Initialize the CSV price feed provider."""
        self._config = config
        self._data_dir = Path(config.data_dir)
        self._supported_symbols = set()
        self._load_supported_symbols()
    
    @property
    def name(self) -> str:
        """Get the provider name."""
        return self._config.name
    
    @property
    def timeframes(self) -> set[CustomTimeframe]:
        """Get the supported timeframes (both supported and native)."""
        timeframes = set(self._config.timeframes.supported_timeframes)
        timeframes.add(self._config.timeframes.native_timeframe)
        return timeframes

    @property 
    def symbols(self) -> set[str]:
        """Get the supported symbols."""
        return self._supported_symbols

    def _load_supported_symbols(self) -> None:
        """Load supported symbols from CSV files with SYMBOL_xxxx naming convention."""
        # Naming convention: SYMBOL_xxxx where SYMBOL is uppercase letters only
        symbol_pattern = re.compile(r'^([A-Z]+)_[A-Za-z0-9_]+$', re.IGNORECASE)
        
        self._supported_symbols = set()
        
        for file_path in self._data_dir.glob(self._config.file_pattern):
            filename = file_path.stem  # Get filename without extension
            
            # Check if filename matches SYMBOL_xxxx pattern (case insensitive)
            match = symbol_pattern.match(filename)
            if match:
                symbol = match.group(1).upper()  # Extract the symbol part and convert to uppercase
                self._supported_symbols.add(symbol)
            else:
                print(f"Warning: Skipping file '{file_path.name}' - doesn't match SYMBOL_xxxx naming convention")
    
    def _find_data_file(self, symbol: str) -> Path:
        """Find the data file for a symbol (case insensitive)."""
        # Try exact match first
        file_path = self._data_dir / f"{symbol}.csv"
        if file_path.exists():
            return file_path
        
        # Try case insensitive match
        for file_path in self._data_dir.glob("*.csv"):
            if file_path.stem.upper() == symbol.upper():
                return file_path
        
        # If still not found, try pattern matching
        for file_path in self._data_dir.glob("*.csv"):
            filename = file_path.stem
            if '_' in filename:
                file_symbol = filename.split('_')[0].upper()
                if file_symbol == symbol.upper():
                    return file_path
        
        raise FileNotFoundError(f"No data file found for symbol {symbol}")
    
    def get_price_data(
        self,
        symbol: str,
        timeframe: CustomTimeframe,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Get price data for a symbol and timeframe.
        
        Args:
            symbol: Symbol to get data for
            timeframe: Timeframe for the data
            start_time: Start time for the data
            end_time: End time for the data
            
        Returns:
            DataFrame with price data
            
        Raises:
            SymbolError: If symbol is not supported
            TimeframeError: If timeframe is not supported
        """
        # Validate symbol
        if symbol not in self._supported_symbols:
            raise SymbolError(f"Symbol {symbol} not supported")
        
        # Validate timeframe
        if timeframe not in self.timeframes:
            raise TimeframeError(f"Timeframe {timeframe} not supported")
        
        # Load data from CSV
        file_path = self._find_data_file(symbol)
        
        df = pd.read_csv(file_path, parse_dates=["timestamp"])
        
        # Filter by date range if provided
        if start_time:
            df = df[df["timestamp"] >= start_time]
        if end_time:
            df = df[df["timestamp"] <= end_time]
        
        # Resample if needed (if timeframe is not native)
        if timeframe != self._config.timeframes.native_timeframe:
            df = self._resample_data(df, timeframe)
        
        return df
    
    def _resample_data(self, df: pd.DataFrame, timeframe: CustomTimeframe) -> pd.DataFrame:
        """Resample data to the requested timeframe."""
        # Set timestamp as index for resampling
        df = df.set_index("timestamp")
        
        # Get resample strategy
        strategy = self._config.timeframes.resample_strategy
        
        # Resample using the strategy
        resampled = df.resample(timeframe.to_pandas_offset()).agg({
            'open': strategy.open,
            'high': strategy.high,
            'low': strategy.low,
            'close': strategy.close,
            'volume': strategy.volume
        })
        
        # Reset index to get timestamp back as column
        return resampled.reset_index()
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is supported by this provider."""
        return symbol in self._supported_symbols 