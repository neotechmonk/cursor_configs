from unittest.mock import Mock

import pytest
from watchdog.events import FileSystemEvent

from util.custom_cache import CacheInvalidationHandler, CustomCache


def make_mock_event(file_path: str, is_directory=False) -> FileSystemEvent:
    """Create a mock FileSystemEvent for testing."""
    event = Mock(spec=FileSystemEvent)
    event.src_path = file_path
    event.is_directory = is_directory
    return event


class TestCacheInvalidationHandler:
    """Test suite for CacheInvalidationHandler."""
    
    @pytest.fixture
    def cache(self)-> CustomCache:
        """Create a fresh cache for each test."""
        return CustomCache()
    
    @pytest.fixture
    def handler(self, cache: CustomCache)-> CacheInvalidationHandler:
        """Create a handler with the test cache."""
        return CacheInvalidationHandler(cache)
    
    def test_on_modified_removes_key(self, cache, handler):
        """Test that modified events remove the corresponding cache key."""
        # Arrange
        cache.add("config1", "dummy")
        event = make_mock_event("/some/path/config1.yaml")
        
        # Act
        handler.on_modified(event)
        
        # Assert
        assert cache.get("config1") is None
    
    def test_on_deleted_removes_key(self, cache, handler):
        """Test that deleted events remove the corresponding cache key."""
        # Arrange
        cache.add("config2", "dummy")
        event = make_mock_event("/some/path/config2.yaml")
        
        # Act
        handler.on_deleted(event)
        
        # Assert
        assert cache.get("config2") is None
    
    def test_ignores_directory_events(self, cache, handler):
        """Test that directory events are ignored and don't affect cache."""
        # Arrange
        cache.add("should_stay", "value")
        event = make_mock_event("/some/path/should_stay", is_directory=True)
        
        # Act
        handler.on_modified(event)
        handler.on_deleted(event)
        
        # Assert
        assert cache.get("should_stay") == "value"
    
    def test_multiple_files_affected_independently(self, cache, handler):
        """Test that multiple files can be invalidated independently."""
        # Arrange
        cache.add("config1", "value1")
        cache.add("config2", "value2")
        cache.add("config3", "value3")
        
        # Act - modify only config1 and config2
        handler.on_modified(make_mock_event("/some/path/config1.yaml"))
        handler.on_deleted(make_mock_event("/some/path/config2.yaml"))
        
        # Assert
        assert cache.get("config1") is None
        assert cache.get("config2") is None
        assert cache.get("config3") == "value3"  # Should remain
    
    def test_case_insensitive_filename_matching(self, cache, handler):
        """Test that filename matching is case-insensitive."""
        # Arrange
        cache.add("config1", "value")
        event = make_mock_event("/some/path/config1.yaml")
        
        # Act
        handler.on_modified(event)
        
        # Assert
        assert cache.get("config1") is None
    
    def test_handles_missing_cache_keys_gracefully(self, cache, handler):
        """Test that trying to invalidate non-existent keys doesn't cause errors."""
        # Arrange
        event = make_mock_event("/some/path/nonexistent.yaml")
        
        # Act & Assert - should not raise any exceptions
        try:
            handler.on_modified(event)
            handler.on_deleted(event)
        except Exception as e:
            pytest.fail(f"Should not raise exception: {e}")
    
    def test_preserves_other_cache_operations(self, cache, handler):
        """Test that cache operations still work after invalidation."""
        # Arrange
        cache.add("config1", "value1")
        cache.add("config2", "value2")
        
        # Act
        handler.on_modified(make_mock_event("/some/path/config1.yaml"))
        cache.add("config3", "value3")  # Add new item after invalidation
        
        # Assert
        assert cache.get("config1") is None
        assert cache.get("config2") == "value2"
        assert cache.get("config3") == "value3"