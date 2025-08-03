from pathlib import Path
from typing import Dict

from core.data_provider.protocol import DataProviderProtocol
from core.data_provider.settings import DataProviderMetadata
from util.custom_cache import Cache
from util.provider_builder import ProviderBuilder


class DataProviderService:
    def __init__(self, config_dir: Path, cache: Cache, registry: Dict[str, DataProviderMetadata] = None):
        self.config_dir = config_dir
        self.cache: Cache = cache
        self.registry: Dict[str, DataProviderMetadata] = registry or {}
    
    def _load_data_provider_by_name(self, name:str) -> DataProviderProtocol:
        config_path:Path = Path(f"{self.config_dir}/{name}.yaml")

        builder = ProviderBuilder[DataProviderProtocol, DataProviderMetadata](config_path=config_path, meta_data=self.registry[name]) 

        provider: DataProviderProtocol =  builder\
            .load_config()\
            .get_provider()\
            .build()
        
        return provider

    def get(self, name: str) -> DataProviderProtocol:
        if not (provider := self.cache.get(name)):
            provider = self._load_data_provider_by_name(name)
            self.cache.add(name, provider)
        return provider

    def get_all(self) -> list[DataProviderProtocol]:
        for path in self.config_dir.glob("*.yaml"):
            name = path.stem
            if not self.cache.get(name):
                self.cache.add(name, self._load_data_provider_by_name(name))
        return list(self.cache.get_all())

    def clear_cache(self) -> None:
        self.cache.clear()