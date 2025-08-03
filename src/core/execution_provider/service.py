from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Self, Union

from pydantic import BaseModel

from core.execution_provider.protocol import ExecutionProviderProtocol
from core.execution_provider.settings import ExecutionProviderMetadata
from util.custom_cache import Cache
from util.yaml_config_loader import load_yaml_config


@dataclass
class ProviderBuilder[P, M]:
    config_path:Path
    meta_data: M
    yaml_config_loader: Callable[...,Union[dict, BaseModel]] = load_yaml_config

    def _load_yaml_config(self)->Self:
        if not isinstance(self. config_path, Path):
            raise ValueError(f"`config_path`, {self.config_path} is not a valid `Path` object")
        
        if not self.config_path.exists():
            raise ValueError(f"`config_path`, {self.config_path} is not exist")
         
        self._config_dict:dict = load_yaml_config(self.config_path)
        return self
    
    def _load_config_raw_model(self)->Self:
        if not all([self._config_dict, isinstance(self._config_dict, dict)]):
            raise ValueError("A valid config must loaded as dict using `load_config()` before calling this method") 
        
        self._raw_config_model = self.meta_data.raw_config(**self._config_dict)
        self._raw_config_model.name = self.config_path.stem

        return self
    
    def _load_config_target_model(self)->Self:
        if not isinstance(self._raw_config_model, self.meta_data.raw_config):
            raise ValueError(f"A valid config must loaded as {type(self.meta_data.raw_config)} using `load_raw_model()` before calling this method") 
        
        self._target_config_model = self.meta_data.target_config(**self._raw_config_model.model_dump())
        return self
    
    def load_config(self)-> Self: 
        self._load_yaml_config()\
            ._load_config_raw_model()\
            ._load_config_target_model()

        return self
    
    def get_provider(self)->Self:
        self._provider = self.meta_data.provider_class(config=self._target_config_model)
        return self
    
    def build(self)-> P:
        return self._provider


class ExecutionProviderService:
    def __init__(self, config_dir: Path, cache: Cache, registry: Dict[str, ExecutionProviderMetadata] = None):
        self.config_dir = config_dir
        self.cache: Cache = cache
        self.registry: Dict[str, ExecutionProviderMetadata] = registry or {}
    
    def _load_execution_provider_by_name_v2(self, name:str) -> ExecutionProviderProtocol:
        config_path:Path = Path(f"{self.config_dir}/{name}.yaml")

        builder = ProviderBuilder[ExecutionProviderProtocol, ExecutionProviderMetadata](config_path=config_path, meta_data=self.registry[name]) 

        return builder\
            .load_config()\
            .get_provider()\
            .build()
            
    def _load_execution_provider_by_name_v1(self, name: str) -> ExecutionProviderProtocol:
        try:
            metadata = self.registry[name]
        except KeyError:
            raise ValueError(f"Unsupported order execution provider: {name}")

        raw_model = load_yaml_config(self.config_dir / f"{name}.yaml", metadata.raw_config)
        raw_model.name = name # set provider name based on the file name 

        target_model = metadata.target_config(**raw_model.model_dump())
        provider = metadata.provider_class(config=target_model)

        if not isinstance(provider, ExecutionProviderProtocol):
            raise TypeError(f"{metadata.provider_class.__name__} must implement {ExecutionProviderProtocol.__name__}")

        return provider

    def get(self, name: str) -> ExecutionProviderProtocol:
        if not (provider := self.cache.get(name)):
            provider = self._load_execution_provider_by_name_v2(name)
            self.cache.add(name, provider)
        return provider

    def get_all(self) -> list[ExecutionProviderProtocol]:
        for path in self.config_dir.glob("*.yaml"):
            name = path.stem
            if not self.cache.get(name):
                self.cache.add(name, self._load_execution_provider_by_name_v2(name))
        return list(self.cache.get_all())

    def clear_cache(self) -> None:
        self.cache.clear()


