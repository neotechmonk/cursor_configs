from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.data_provider.protocol import DataProviderProtocol
from core.execution_provider.protocol import ExecutionProvider
from core.time import CustomTimeframe


class SymbolConfigModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        populate_by_name=True  # <- allows using either field name or alias
    )

    symbol: str
    data_provider: DataProviderProtocol = Field(..., alias="data-provider")
    execution_provider: ExecutionProvider = Field(..., alias="execution-provider")
    timeframe: CustomTimeframe
    enabled: bool = True
    

class RawSymbolConfig(BaseModel):
    """ Models raw symbol config from yaml file
    E.f.
        AAPL:
            providers:
                data: "csv"
                execution: "ib"
            timeframe: "5m"
            enabled: true

    """
    providers: dict[Literal['data', 'execution'], str] = Field(
        ..., description="Raw string provider identifiers (e.g., 'csv', 'ib'); resolved to service objects later"
    )
    timeframe: str = Field(
        ..., description="Timeframe as a string (e.g., '5m'); to be converted into a CustomTimeframe later"
    )
    enabled: bool = Field(default=True, description="Whether the symbol is active")
    
    symbol: Optional[str] = Field(
        default=None,
        description="Injected from YAML key (e.g., 'AAPL'); not part of the YAML value body"
    )


def parse_raw_symbol_configs(raw_dict: dict[str, dict]) -> list[RawSymbolConfig]:
    """Convert raw YAML dict into a list of validated RawSymbolConfig models."""
    return [
        RawSymbolConfig(**value, symbol=key)
        for key, value in raw_dict.items()
    ]


def resolve_symbol_config_from_raw_model(
    raw: RawSymbolConfig,
    data_provider_service, 
    execution_provider_service
) -> SymbolConfigModel:
    try:
        return SymbolConfigModel(
            symbol=raw.symbol,
            data_provider=data_provider_service.get(raw.providers["data"]) ,
            execution_provider=execution_provider_service.get(raw.providers["execution"]) ,
            timeframe=CustomTimeframe(raw.timeframe),
            enabled=raw.enabled
        )
    except Exception as e:
        raise ValueError(f"Error resolving symbol config from raw model: {e}")

