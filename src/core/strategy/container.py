from dependency_injector import containers, providers

from core.strategy.hydration import hydrate_strategy_config
from core.strategy.service import StrategyService
from core.strategy.settings import StrategySettings
from core.strategy.steps.container import StrategyStepContainer
from util.custom_cache import CacheInvalidationHandler, ScopedCacheView, WatchedCache

NAMESPACE = __name__


class StrategyContainer(containers.DeclarativeContainer):
    """Container for managing strategy dependencies."""

    # Configuration dependency (injected externally)
    settings = providers.Dependency(instance_of=StrategySettings, default=StrategySettings())

    cache_backend = providers.Singleton(WatchedCache)
    # -- Isolates cache for the data provider
    scoped_cache = providers.Factory(
        ScopedCacheView,
        cache_backend,  
        NAMESPACE)      
    
    observer = providers.Resource(
        CacheInvalidationHandler.start,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=scoped_cache)

    # Now you can call init_resources on this instance
    steps_container = providers.Container(
        StrategyStepContainer,
    )

    # Ensure StrategyStepContainer resources are initialised
    init_steps_caching = providers.Resource(steps_container.provided.init_resources)

    service = providers.Singleton(
        StrategyService,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=scoped_cache,
        model_hydration_fn=providers.Object(hydrate_strategy_config),        
        steps_registry=steps_container.provided.service(), 
    )
