"""Root container for managing all dependencies."""

import logging

from dependency_injector import containers, providers

from core.app.logging import load_logging_config
from core.app.settings import AppSettings
from core.data_provider.container import DataProviderContainer
from core.execution_provider.container import ExecutionProviderContainer
from core.portfolio.container import PortfolioContainer
from core.sessions.container import TradingSessionContainer
from core.strategy.container import StrategyContainer


class AppContainer(containers.DeclarativeContainer):
    """Root container that manages all dependencies."""
    wiring_config = containers.WiringConfiguration(packages=[
        "core.data_provider",
        "core.portfolio",
        "core.sessions",
        "core.execution_provider",
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
        settings=settings.provided.data_provider
    )
    
    strategy = providers.Container(
        StrategyContainer,
        settings=settings.provided.strategy  
    )

    portfolio = providers.Container(
        PortfolioContainer,
        settings=settings.provided.portfolio  
    )

    # Execution provider container
    execution_provider = providers.Container(
        ExecutionProviderContainer,
        settings=settings.provided.execution_provider
    )

    # Add sessions container
    sessions = providers.Container(
        TradingSessionContainer,
        settings=settings.provided.sessions,
        data_provider_service=data_provider.service,
        execution_provider_service=execution_provider.service,
        portfolio_service=portfolio.service
    )
