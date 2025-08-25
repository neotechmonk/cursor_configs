from dependency_injector import containers, providers

from core.sessions.session import TradingSessionService, TradingSessionSettings


class TradingSessionContainer(containers.DeclarativeContainer):
    """Trading session DI container."""
    
    # Configuration
    settings = providers.Dependency(instance_of=TradingSessionSettings)
    
    # Dependencies
    data_provider_service = providers.Dependency()
    execution_provider_service = providers.Dependency()
    portfolio_service = providers.Dependency()
    strategy_service = providers.Dependency()
    
    # Service Layer - simpler approach
    service = providers.Singleton(
        TradingSessionService,
        sessions_dir=providers.Callable(lambda s: s.config_dir, settings),
        data_provider_service=data_provider_service,
        execution_provider_service=execution_provider_service,
        portfolio_service=portfolio_service,
        strategy_service=strategy_service
    )