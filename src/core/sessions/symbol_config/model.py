from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.data_provider.protocol import (
    DataProviderProtocol,
    DataProviderServiceProtocol,
)
from core.execution_provider.protocol import (
    ExecutionProviderProtocol,
    ExecutionProviderServiceProtocol,
)
from core.strategy.protocol import StrategyProtocol, StrategyServiceProtocol
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
    """ Models raw symbol config from yaml file
    E.f.
        AAPL:
            strategy: "sample_strategy"
            providers:
                data: "csv"
                execution: "ib"
            timeframe: "5m"
            enabled: true

    """

    providers: dict[Literal['data', 'execution'], str] = Field(
        ..., description="Provider names under config/providers/data and config/providers/execution"
    )
    timeframe: str = Field(
        ..., description="Timeframe as a string (e.g., '5m'); to be converted into a CustomTimeframe later"
    )
    enabled: bool = Field(default=True, description="Whether the symbol is active")
    
    symbol: Optional[str] = Field(
        default=None,
        min_length=1,
        pattern=r"\S",
        description="Injected from YAML key (e.g., 'AAPL'); not part of the YAML value body"
    )
    strategy: str = Field(
        min_length=1,
        pattern=r"\S",
        description="Strategy name under `config/strategies`"
    )

    @field_validator('providers')
    @classmethod
    def all_required_providers(cls, v):
        if  {'data', 'execution'} - set(v.keys()):
            raise ValueError(f"Missing provider/s: Expected {allowed_keys}, got {v.keys()}")
        return v

"""replaced with transformers"""
# def resolve_symbol_config_from_raw_model(
#     raw: RawSymbolConfig,
#     data_provider_service: DataProviderServiceProtocol, 
#     execution_provider_service: ExecutionProviderServiceProtocol,
#     strategy_service: StrategyServiceProtocol,    
# ) -> SymbolConfigModel:
    
#     try:
#         return SymbolConfigModel(
#             symbol=raw.symbol,
#             strategy=strategy_service.get(raw.strategy),
#             data_provider=data_provider_service.get(raw.providers["data"]) ,
#             execution_provider=execution_provider_service.get(raw.providers["execution"]) ,
#             timeframe=CustomTimeframe(raw.timeframe),
#             enabled=raw.enabled
#         )
#     except Exception as e:
#         raise ValueError(f"Error resolving symbol config from raw model: {e}")

