"""Root container for managing all dependencies."""

import logging

from dependency_injector import containers, providers

from core.app.logging import configure_logging
from core.app.settings import AppSettings
from core.data_provider.container import DataProviderContainer
from core.portfolio.container import PortfolioContainer


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
        configure_logging,
        settings=settings.provided.logging,  # Access the actual LoggingSettings object
    )

    logger = providers.Factory(logging.getLogger, name="core")

    # Subcontainers
    data_provider = providers.Container(
        DataProviderContainer,
        settings=settings.provided.portfolio  # Access the actual PortfolioSettings object
    )

    portfolio = providers.Container(
        PortfolioContainer,
        settings=settings.provided.portfolio  # Access the actual PortfolioSettings object
    )
