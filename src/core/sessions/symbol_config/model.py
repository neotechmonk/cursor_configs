"""Symbol configuration models for the new list-based YAML structure.

This module defines the data models used for symbol configuration in the
updated session configuration system. The new approach uses explicit
symbol fields in list-based structures instead of key-value mapping.

Key Changes:
- RawSymbolConfig now expects explicit 'symbol' field
- Symbols are processed as list items rather than dict keys
- Improved validation and error handling
- Better support for symbol metadata and properties

The models support both the new list-based structure and maintain
compatibility with existing symbol resolution logic.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.data_provider.protocol import DataProviderProtocol
from core.execution_provider.protocol import ExecutionProviderProtocol
from core.strategy.protocol import StrategyProtocol
from core.time import CustomTimeframe


class SymbolConfigModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        populate_by_name=True  # <- allows using either field name or alias
    )

    symbol: str 
    data_provider: DataProviderProtocol = Field(..., alias="data-provider")
    execution_provider: ExecutionProviderProtocol = Field(..., alias="execution-provider")
    timeframe: CustomTimeframe
    enabled: bool = True
    strategy: StrategyProtocol

    @field_validator('timeframe', mode='before')
    @classmethod
    def validate_timeframe(cls, v):
        if isinstance(v, str):
            return CustomTimeframe(v)
        
        return v


class RawSymbolConfig(BaseModel):
    """Models raw symbol config from YAML file with explicit symbol field.
    
    This model is used in the new list-based symbols structure where each
    symbol configuration includes an explicit 'symbol' field instead of
    being keyed by the symbol name.
    
    Example YAML structure:
        symbols:
          - symbol: AAPL
            strategy: "sample_strategy"
            providers:
              data: "csv"
              execution: "ib"
            timeframe: "5m"
            enabled: true
          - symbol: SPY
            strategy: "sample_strategy"
            providers:
              data: "yahoo"
              execution: "ib"
            timeframe: "1d"
            enabled: true
    """

    providers: dict[Literal['data', 'execution'], str] = Field(
        ..., description="Provider names under config/providers/data and config/providers/execution"
    )
    timeframe: str = Field(
        ..., description="Timeframe as a string (e.g., '5m'); to be converted into a CustomTimeframe later"
    )
    enabled: bool = Field(default=True, description="Whether the symbol is active")
    
    symbol: str = Field(
        min_length=1,
        pattern=r"\S",
    )
    strategy: str = Field(
        min_length=1,
        pattern=r"\S",
        description="Strategy name under `config/strategies`"
    )

    @field_validator('providers')
    @classmethod
    def all_required_providers(cls, v):
        allowed_keys = {'data', 'execution'}
        if allowed_keys - set(v.keys()):
            raise ValueError(f"Missing provider/s: Expected {allowed_keys}, got {v.keys()}")
        return v

