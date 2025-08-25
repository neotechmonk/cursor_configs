from pathlib import Path
from typing import Dict

from core.execution_provider.protocol import ExecutionProviderProtocol
from core.execution_provider.settings import ExecutionProviderMetadata
from util.custom_cache import Cache
from util.provider_builder import ProviderBuilder


class ExecutionProviderService:
    def __init__(self, config_dir: Path, cache: Cache, registry: Dict[str, ExecutionProviderMetadata] = None):
        self.config_dir = config_dir
        self.cache: Cache = cache
        self.registry: Dict[str, ExecutionProviderMetadata] = registry or {}
    
    def _load_execution_provider_by_name(self, name:str) -> ExecutionProviderProtocol:
        config_path:Path = Path(f"{self.config_dir}/{name}.yaml")

        builder = ProviderBuilder[ExecutionProviderProtocol, ExecutionProviderMetadata](config_path=config_path, meta_data=self.registry[name]) 

        return builder\
            .load_config()\
            .get_provider()\
            .build()
            
    def get(self, name: str) -> ExecutionProviderProtocol:
        if not (provider := self.cache.get(name)):
            provider = self._load_execution_provider_by_name(name)
            self.cache.add(name, provider)
        return provider

    def get_all(self) -> list[ExecutionProviderProtocol]:
        for path in self.config_dir.glob("*.yaml"):
            name = path.stem
            if not self.cache.get(name):
                self.cache.add(name, self._load_execution_provider_by_name(name))
        return list(self.cache.get_all())

    def clear_cache(self) -> None:
        self.cache.clear()


