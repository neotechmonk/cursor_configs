from typing import Dict
from dependency_injector import containers, providers
from pathlib import Path

from core.portfolio.portfolio import Portfolio, PortfolioConfig, PortfolioSettings
from core.portfolio.protocol import PortfolioProtocol
from loaders.generic import load_yaml_config


class PortfolioContainer(containers.DeclarativeContainer):
    """Container for managing portfolio lifecycle and dependencies."""
    
    config = providers.Configuration()
    settings = providers.Dependency(instance_of=PortfolioSettings)

    # DI-managed cache: shared dictionary for caching portfolio instances
    portfolio_cache = providers.Singleton(dict)

    def _load_portfolio_by_name(self, name: str) -> PortfolioProtocol:
        config_path = self.settings().config_dir / f"{name}.yaml"
        portfolio_config = load_yaml_config(config_path, PortfolioConfig)

        return Portfolio(
            name=name,
            description=portfolio_config.description,
            initial_capital=portfolio_config.initial_capital
        )

    def get(self, name: str) -> PortfolioProtocol:
        cache: Dict[str, PortfolioProtocol] = self.portfolio_cache()

        if name in cache:
            return cache[name]

        portfolio = self._load_portfolio_by_name(name)
        cache[name] = portfolio
        return portfolio

    def get_all(self) -> list[PortfolioProtocol]:
        cache = self.portfolio_cache()
        for yaml_file in self.settings().config_dir.glob("*.yaml"):
            name = yaml_file.stem
            if name not in cache:
                cache[name] = self._load_portfolio_by_name(name)
        return list(cache.values())

    def clear_cache(self) -> None:
        self.portfolio_cache().clear()