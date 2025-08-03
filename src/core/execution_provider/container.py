
from dependency_injector import containers, providers

from core.execution_provider.service import ExecutionProviderService
from core.execution_provider.settings import ExecutionProviderSettings
from util.custom_cache import CacheInvalidationHandler, ScopedCacheView, WatchedCache


class ExecutionProviderContainer(containers.DeclarativeContainer):
    NAMESPACE = __name__
    settings: ExecutionProviderSettings = providers.Configuration()

    #Cache management
    # -- Cache object
    cache_backend = providers.Singleton(WatchedCache)
    # -- Isolates cache for the data provider
    scoped_cache = providers.Factory(
        ScopedCacheView,
        cache_backend,  # Fixed: cache object first
        NAMESPACE)      # Fixed: namespace second
    observer = providers.Resource(
        CacheInvalidationHandler.start,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=scoped_cache)
    
    service = providers.Singleton(
        ExecutionProviderService,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=scoped_cache,
        registry=providers.Callable(lambda s: s.providers, settings),
    )
