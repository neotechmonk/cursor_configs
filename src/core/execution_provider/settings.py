import importlib
from pathlib import Path
from typing import Dict, Type, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings

from core.execution_provider.protocol import ExecutionProviderProtocol


class ExecutionProviderMetadata(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="allow")
    raw_config: Type[BaseModel]
    target_config: Type[BaseModel]
    provider_class: Type[ExecutionProviderProtocol]

    @staticmethod
    def _resolve_class(path: Union[str, Type]) -> Type:
        if isinstance(path, str):
            module_name, class_name = path.rsplit(".", 1)
            return getattr(importlib.import_module(module_name), class_name)
        return path

    @field_validator("raw_config", "target_config", "provider_class", mode="before")
    @classmethod
    def resolve_class(cls, value):
        return cls._resolve_class(value)
    

class ExecutionProviderSettings(BaseSettings):
    """Execution provider-specific settings from app configuration."""
    config_dir: Path = Field(default=Path("configs/providers/execution"))

    providers: Dict[str, ExecutionProviderMetadata] = Field(default_factory=dict)
    