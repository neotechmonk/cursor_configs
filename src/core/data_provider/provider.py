from pathlib import Path

from pydantic import BaseSettings, Field

from core.data_provider.protocol import DataProviderProtocol
from util.custom_cache import Cache


class DataProviderSettings(BaseSettings):
    """Data provider-specific settings from app configuration."""
    config_dir: Path = Field(default=Path("configs/providers/data"))


@dataclass
class DataProviderService:
    def __init__(self, config_dir: Path, cache: Cache):
        self.config_dir = config_dir
        self.cache: Cache = cache

    def _load_data_provider_by_name(self, name: str) -> DataProviderProtocol:
        config = load_yaml_config(self.config_dir, DataProviderConfig)
        return DataProvider(name=name, description=config.description, initial_capital=config.initial_capital)

    def get(self, name: str) -> DataProviderProtocol:
        if name not in self.cache:
            self.cache[name] = self._load_data_provider_by_name(name)
        return self.cache[name]

    def get_all(self) -> list[DataProviderProtocol]:
        for file in self.settings.config_dir.glob("*.yaml"):
            name = file.stem
            if name not in self.cache:
                self.cache[name] = self._load_data_provider_by_name(name)
        return list(self.cache.values())

    def clear_cache(self) -> None:
        self.cache.clear()