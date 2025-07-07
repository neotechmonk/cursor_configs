import os
import tempfile
from pathlib import Path
from time import sleep
from unittest.mock import MagicMock

import pytest
from dependency_injector import containers, providers

from util.custom_cache import CacheInvalidationHandler, ScopedCacheView, WatchedCache


#service.py
class MockedService:
    def __init__(self, config_dir, cache: ScopedCacheView):
        self.config_dir = config_dir
        self.cache = cache
        self.load_called_with = []
    
    def get(self, name: str) -> str:
        self.load_called_with.append(name)
        return self.cache.get(name) or f"mocked:{name}"
    
    def get_all(self):
        return self.cache.keys()

    def clear_cache(self):
        self.cache.clear()


# container.py
class MockedContainer(containers.DeclarativeContainer):
    settings = providers.Dependency()
    cache_backend = providers.Singleton(WatchedCache)
    
    scoped_cache = providers.Factory(
        ScopedCacheView,
        "data_provider",  # <-- positional
        cache_backend
    )
    service = providers.Singleton(
        MockedService,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=scoped_cache,
    )
  
    observer = providers.Resource(
        CacheInvalidationHandler.start,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=scoped_cache)


def test_data_provider_container_with_mock_settings():
    # Arrange: Create mock settings and mock cache
    mock_settings = MagicMock()
    mock_settings.config_dir = Path("/fake/config")

    mock_cache = MagicMock()
    
    # Set up the container
    container = MockedContainer(
        settings=mock_settings,
        cache_backend=mock_cache,
    )

    # Override service to prevent real __init__ logic if needed
    mock_service = MagicMock(spec=MockedService)
    container.service.override(providers.Object(mock_service))

    # Act: Resolve the service via container
    resolved = container.service()

    # Assert: It should return the mocked service
    assert resolved is mock_service

    # Optional: Validate mock calls
    resolved.get.assert_not_called()


def test_data_provider_service_integration():
    # Given
    container = MockedContainer()
    container.settings.override(MagicMock(config_dir=Path("/tmp/yaml_dir")))
    
    # When
    service = container.service()

    # Then
    assert isinstance(service, MockedService)
    assert service.config_dir == Path("/tmp/yaml_dir")
    assert isinstance(service.cache, ScopedCacheView)


@pytest.mark.xfail(reason="Unable to validate observer is started")
def test_cache_invalidator_is_started(monkeypatch):
    # Arrange
    mock_start = MagicMock()
    mock_observer = MagicMock()
    mock_start.return_value = mock_observer
    monkeypatch.setattr(CacheInvalidationHandler, "start", mock_start)

    # Create and configure container
    container = MockedContainer()
    mock_settings = MagicMock()
    mock_settings.config_dir = Path("/fake/config")
    container.settings.override(mock_settings)
    
    cache = WatchedCache()
    container.cache_backend.override(cache)

    # Act: Initialize resources (this starts the observer)
    container.init_resources()

    # Assert: The start method should be called with correct parameters
    mock_start.assert_called_once_with(
        config_dir=mock_settings.config_dir,
        cache=cache,
    )
    
    # # Verify the observer was created
    assert container.observer() is mock_observer


def test_file_deletion_invalidates_cache():
    # Setup: Create a real file in a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        config_file = config_dir / "test_config.yaml"

        backend = WatchedCache()
        scoped_cache = ScopedCacheView( cache=backend, namespace="data_provider",)  # ✅ provide namespace

        observer = CacheInvalidationHandler.start(config_dir=config_dir, cache=scoped_cache)

        # Create the dummy file
        config_file.write_text("dummy: config")

        # Add to namespaced cache
        scoped_cache.add("test_config", {"mock": "data"})

        assert scoped_cache.get("test_config") is not None

        try:
            print("\nBefore removing the yaml file:", scoped_cache.get("test_config"))

            if config_file.exists():
                print("Removing file")
                os.remove(config_file)

            # Wait for observer to detect the deletion
            sleep(1.0)

            # ✅ This now uses ScopedCacheView which only needs key
            assert scoped_cache.get("test_config") is None
        finally:
            observer.stop()
            observer.join()
            print("....After removing the yaml file :" + str(scoped_cache.get(key="test_config")))
    