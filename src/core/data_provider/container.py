
from dependency_injector import containers, providers

from core.data_provider.provider import DataProviderService
from core.data_provider.settings import DataProviderSettings
from util.custom_cache import CacheInvalidationHandler, ScopedCacheView, WatchedCache


class DataProviderContainer(containers.DeclarativeContainer):
    NAMESPACE = __name__
    settings: DataProviderSettings = providers.Configuration()

    #Cache management
    # -- Cache object
    cache_backend = providers.Singleton(WatchedCache)
    # -- Isolates cache for the data provider
    scoped_cache = providers.Factory(
        ScopedCacheView,
        NAMESPACE,  
        cache_backend)
    observer = providers.Resource(
        CacheInvalidationHandler.start,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=scoped_cache)
    
    service = providers.Singleton(
        DataProviderService,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=scoped_cache,
        registry=providers.Callable(lambda s: s.providers, settings),
    )
