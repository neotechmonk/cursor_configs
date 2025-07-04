from typing import Dict

from dependency_injector import containers, providers

from core.portfolio.portfolio import Portfolio, PortfolioConfig, PortfolioSettings
from core.portfolio.protocol import PortfolioProtocol
from loaders.generic import load_yaml_config


class PortfolioService:
    def __init__(self, settings: PortfolioSettings, cache: Dict[str, PortfolioProtocol]):
        self.settings = settings
        self.cache = cache

    def _load_portfolio_by_name(self, name: str) -> PortfolioProtocol:
        path = self.settings.config_dir / f"{name}.yaml"
        config = load_yaml_config(path, PortfolioConfig)
        return Portfolio(name=name, description=config.description, initial_capital=config.initial_capital)

    def get(self, name: str) -> PortfolioProtocol:
        if name not in self.cache:
            self.cache[name] = self._load_portfolio_by_name(name)
        return self.cache[name]

    def get_all(self) -> list[PortfolioProtocol]:
        for file in self.settings.config_dir.glob("*.yaml"):
            name = file.stem
            if name not in self.cache:
                self.cache[name] = self._load_portfolio_by_name(name)
        return list(self.cache.values())

    def clear_cache(self) -> None:
        self.cache.clear()


class PortfolioContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings = providers.Dependency(instance_of=PortfolioSettings)
    portfolio_cache = providers.Singleton(dict)

    service = providers.Factory(
        PortfolioService,
        settings=settings,
        cache=portfolio_cache,
    )