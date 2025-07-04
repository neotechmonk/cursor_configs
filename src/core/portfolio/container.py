
from dependency_injector import containers, providers

from core.portfolio.portfolio import PortfolioService, PortfolioSettings


class PortfolioContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings = providers.Dependency(instance_of=PortfolioSettings)
    portfolio_cache = providers.Singleton(dict)

    service = providers.Factory(
        PortfolioService,
        settings=settings,
        cache=portfolio_cache,
    )