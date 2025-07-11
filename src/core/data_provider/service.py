from pathlib import Path
from typing import Dict

from core.data_provider.protocol import DataProviderProtocol
from core.data_provider.settings import DataProviderMetadata
from util.yaml_config_loader import load_yaml_config
from util.custom_cache import Cache


class DataProviderService:
    def __init__(self, config_dir: Path, cache: Cache, registry: Dict[str, DataProviderMetadata] = None):
        self.config_dir = config_dir
        self.cache: Cache = cache
        self.registry: Dict[str, DataProviderMetadata] = registry or {}

    def _load_data_provider_by_name(self, name: str) -> DataProviderProtocol:
        """
        Load a data provider by name.
        """
        try:
            metadata = self.registry[name]
        except KeyError:
            raise ValueError(f"Unsupported data provider: {name}")

        raw_model = load_yaml_config(self.config_dir / f"{name}.yaml", metadata.raw_config)
        raw_model.name = name

        target_model = metadata.target_config(**raw_model.model_dump())
        provider = metadata.provider_class(config=target_model)

        if not isinstance(provider, DataProviderProtocol):
            raise TypeError(f"{metadata.provider_class.__name__} must implement DataProviderProtocol")

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