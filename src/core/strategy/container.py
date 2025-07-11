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
    settings = providers.Dependency(instance_of=StrategySettings)  # noqa: F821

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

    steps_registry = StrategyStepContainer.service 
    model_hydration_fn = providers.Object(hydrate_strategy_config) 
    service = providers.Singleton(
        StrategyService,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=scoped_cache,
        model_hydration_fn=model_hydration_fn,
        steps_registry=steps_registry)