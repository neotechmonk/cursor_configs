"""Root container for managing all dependencies."""

import logging

from dependency_injector import containers, providers

from core.app.logging import load_logging_config
from core.app.settings import AppSettings
from core.data_provider.container import DataProviderContainer
from core.portfolio.container import PortfolioContainer
from core.sessions.container import TradingSessionContainer
from core.strategy.container import StrategyContainer
from tests.mocks.providers import MockIBExecutionProvider, MockAlpacaExecutionProvider


class MockExecutionProviderService:
    """Temporary mock execution provider service."""
    
    def __init__(self):
        self._providers = {
            "csv": MockIBExecutionProvider(),  # Use CSV as IB
            "yahoo": MockAlpacaExecutionProvider(),  # Use Yahoo as Alpaca
            "ib": MockIBExecutionProvider(),
            "alpaca": MockAlpacaExecutionProvider(),
        }
    
    def get(self, name: str):
        if name not in self._providers:
            # Fallback to IB for unknown providers
            return MockIBExecutionProvider()
        return self._providers[name]
    
    def get_all(self):
        return list(self._providers.values())


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

    # Mock execution provider service
    execution_provider = providers.Singleton(MockExecutionProviderService)

    # Add sessions container
    sessions = providers.Container(
        TradingSessionContainer,
        settings=settings.provided.sessions,
        data_provider_service=data_provider.service,
        execution_provider_service=execution_provider,
        portfolio_service=portfolio.service
    )
