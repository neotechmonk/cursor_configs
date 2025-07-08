from pathlib import Path

from pydantic import BaseSettings, Field

from core.data_provider.csv import CSVPriceFeedProvider, RawCSVPriceFeedConfig, resolve_csv_pricefeed_config
from core.data_provider.protocol import DataProviderProtocol
from loaders.generic import load_yaml_config
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
        match name:
            case "csv":
                raw_model: RawCSVPriceFeedConfig = load_yaml_config(self.config_dir / f"{name}.yaml", RawCSVPriceFeedConfig)
                raw_model.name = name
                target_model: CSVPriceFeedProvider = resolve_csv_pricefeed_config(raw_model)
                return target_model
            case _:
                raise ValueError(f"Unsupported data provider: {name}")

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