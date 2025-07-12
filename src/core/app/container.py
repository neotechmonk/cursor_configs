"""Root container for managing all dependencies."""

import logging

from dependency_injector import containers, providers

from core.app.logging import load_logging_config
from core.app.settings import AppSettings
from core.data_provider.container import DataProviderContainer
from core.strategy.container import StrategyContainer


class AppContainer(containers.DeclarativeContainer):
    """Root container that manages all dependencies."""
    wiring_config = containers.WiringConfiguration(packages=[
        "core.data_provider",
        "core.portfolio",
        "core.sessions",
    ])
    """
    AppSettings loads other settings like logging, portfolio, sessions, etc.
    AppSettings relies on the env var `APP_SETTINGS_PATH` settings.json file.
    """
    settings = providers.Singleton(AppSettings)
    
    # Shared resources
    logging_config = providers.Resource(
        load_logging_config,
        config_path=settings.provided.logging.config_path,
    )

    logger = providers.Factory(logging.getLogger, name="core")

    # Subcontainers
    data_provider = providers.Container(
        DataProviderContainer,
        settings=settings.provided.data_provider  # Fixed: was portfolio, should be data_provider
    )

    strategy = providers.Container(
        StrategyContainer,
        settings=settings.provided.strategy  
    )

    # portfolio = providers.Container(
    #     PortfolioContainer,
    #     settings=settings.provided.portfolio  # Access the actual PortfolioSettings object
    # )
