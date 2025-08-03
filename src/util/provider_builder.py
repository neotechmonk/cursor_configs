from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Self, TypeVar, Union

from pydantic import BaseModel

from core.data_provider.protocol import DataProviderProtocol
from core.data_provider.settings import DataProviderMetadata
from core.execution_provider.protocol import ExecutionProviderProtocol
from core.execution_provider.settings import ExecutionProviderMetadata
from util.yaml_config_loader import load_yaml_config

P = TypeVar("P", bound=Union[ExecutionProviderProtocol, DataProviderProtocol]) 
M = TypeVar("M", bound=Union[ExecutionProviderMetadata, DataProviderMetadata])


@dataclass
class ProviderBuilder[P, M]:
    config_path: Path
    meta_data: M
    yaml_config_loader: Callable[..., Union[dict, BaseModel]] = load_yaml_config

    def __post_init__(self):
        self._config_dict = None
        self._raw_config_model = None
        self._target_config_model = None
        self._provider = None

    def _load_yaml_config(self) -> Self:
        if not isinstance(self.config_path, Path):
            raise ValueError(f"`config_path`, {self.config_path} is not a valid `Path` object")
        
        if not self.config_path.exists():
            raise ValueError(f"`config_path`, {self.config_path} is not exist")
         
        self._config_dict: dict = load_yaml_config(self.config_path)
        return self
    
    def _load_config_raw_model(self) -> Self:
        if not all([self._config_dict, isinstance(self._config_dict, dict)]):
            raise ValueError("A valid config must loaded as dict using `load_config()` before calling this method") 
        
        self._raw_config_model = self.meta_data.raw_config(**self._config_dict)
        self._raw_config_model.name = self.config_path.stem

        return self
    
    def _load_config_target_model(self) -> Self:
        if not isinstance(self._raw_config_model, self.meta_data.raw_config):
            raise ValueError("Config must be loaded as dict before calling `_load_config_raw_model()`")
        
        self._target_config_model = self.meta_data.target_config(**self._raw_config_model.model_dump())
        return self
    
    def load_config(self) -> Self:
        return (
            self._load_yaml_config()
                ._load_config_raw_model()
                ._load_config_target_model()
        )
    
    def get_provider(self) -> Self:
        if not self._target_config_model:
            raise ValueError("Target config model not loaded. Call `load_config()` first.")
        
        self._provider = self.meta_data.provider_class(config=self._target_config_model)
        return self
    
    def build(self) -> P:
        if not self._provider:
            raise ValueError("Provider not initialized. Call `get_provider()` first.")
        return self._provider
        return self._provider