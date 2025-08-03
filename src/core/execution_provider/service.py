from pathlib import Path
from typing import Dict

from core.execution_provider.protocol import ExecutionProviderProtocol
from core.execution_provider.settings import ExecutionProviderMetadata
from util.custom_cache import Cache
from util.provider_builder import ProviderBuilder
from util.yaml_config_loader import load_yaml_config


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


