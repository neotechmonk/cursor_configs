from time import sleep
import os
from pathlib import Path
import tempfile
from typing import Dict
from unittest.mock import MagicMock

from dependency_injector import containers, providers

from util.custom_cache import CacheInvalidationHandler, CustomCache
import pytest

#service.py
class MockedService:
    def __init__(self, config_dir, cache: Dict[str, str]):
        self.config_dir = config_dir
        self.cache = cache
        self.load_called_with = []
    
    def get(self, name: str) -> str:
        self.load_called_with.append(name)
        return self.cache.get(name, f"mocked:{name}")
    
    def get_all(self):
        return list(self.cache.values())

    def clear_cache(self):
        self.cache.clear()


# container.py
class MockedContainer(containers.DeclarativeContainer):
    settings = providers.Dependency()
    data_provider_cache = providers.Singleton(dict)
    
    service = providers.Singleton(
        MockedService,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=data_provider_cache,
    )

    # Define observer as a resource
    observer = providers.Resource(
        CacheInvalidationHandler.start,
        config_dir=providers.Callable(lambda s: s.config_dir, settings),
        cache=data_provider_cache,
    )


def test_data_provider_container_with_mock_settings():
    # Arrange: Create mock settings and mock cache
    mock_settings = MagicMock()
    mock_settings.config_dir = Path("/fake/config")

    mock_cache = MagicMock()
    
    # Set up the container
    container = MockedContainer(
        settings=mock_settings,
        data_provider_cache=mock_cache,
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
    assert isinstance(service.cache, dict)


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
    
    cache = CustomCache()
    container.data_provider_cache.override(cache)

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
        # config_file_wrong = Path(tmpdir) / "test_config-wrong.yaml"

        cache = CustomCache()        
        observer = CacheInvalidationHandler.start(config_dir=config_dir, cache=cache)

        # Create a dummy YAML file
        config_file.write_text("dummy: config")

        # Create cache and insert the
        cache.add("test_config", {"mock": "data"})

        assert cache.get("test_config") is not None  # Precondition


        try:
            print("\nBefore removing the yaml file :" + str(cache.get("test_config")))
            # Delete the file to trigger the handler
            if config_file.exists():
                print("Removing file")
                os.remove(config_file)
                print("....After removing the yaml file :" + str(cache.get("test_config")))

            # Allow time for watchdog to pick up the event
            sleep(1.0)  # May need to be adjusted based on platform/CI speed

            
            # Verify that cache is invalidated
            assert cache.get("test_config") is None
        finally:
            print("....AfBefore  stopping the observer  :" + str(cache.get("test_config")))
            observer.stop()
            observer.join()
            print("....After stopping the observer  :" + str(cache.get("test_config")))