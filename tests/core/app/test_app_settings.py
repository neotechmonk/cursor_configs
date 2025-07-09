import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from core.app.settings import AppSettings


@pytest.fixture
def temp_settings_file():
    """Create a temporary settings.json file for testing."""
    config_data = {
        "portfolio": {
            "config_dir": "json/portfolios"
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = Path(f.name)

    yield temp_file

    # Cleanup
    temp_file.unlink(missing_ok=True)


def test_app_settings_loads_from_settings_json():
    """Test that AppSettings loads from configs/settings.json automatically."""
    settings = AppSettings()
    
    # Verify that settings are loaded from the JSON file
    assert settings.logging.config_path == Path("configs/logging.json")
    assert settings.portfolio.config_dir == Path("configs/portfolios")
    assert settings.sessions.config_dir == Path("configs/sessions")


def test_app_settings_with_custom_json():
    """Test that AppSettings can load from a custom JSON file when passed explicitly."""
    # Create a custom config dict
    config_dict = {
        "portfolio": {
            "config_dir": "custom/portfolios"
        },
        "sessions": {
            "config_dir": "custom/sessions"
        }
    }

    # Pass the config dict explicitly - this should override the JSON file
    settings = AppSettings(**config_dict)

    # The explicitly passed values should take precedence
    assert settings.portfolio.config_dir == Path("custom/portfolios")
    assert settings.sessions.config_dir == Path("custom/sessions")


def test_app_settings_from_dict():
    """Test that AppSettings can be created from dictionary."""
    config_dict = {
        "portfolio": {
            "config_dir": "dict/portfolios"
        },
        "sessions": {
            "config_dir": "dict/sessions"
        }
    }

    settings = AppSettings(**config_dict)
    assert settings.portfolio.config_dir == Path("dict/portfolios")
    assert settings.sessions.config_dir == Path("dict/sessions")


def test_app_settings_priority_order():
    """Test that AppSettings respects the correct priority order."""
    # Set environment variables
    env_vars = {
        "PORTFOLIO__CONFIG_DIR": "env/portfolios",
        "SESSIONS__CONFIG_DIR": "env/sessions"
    }
    
    with patch.dict(os.environ, env_vars):
        # Pass explicit values - these should have highest priority
        explicit_config = {
            "portfolio": {"config_dir": "explicit/portfolios"},
            "sessions": {"config_dir": "explicit/sessions"}
        }
        
        settings = AppSettings(**explicit_config)
        
        # Explicit values should override environment variables
        assert settings.portfolio.config_dir == Path("explicit/portfolios")
        assert settings.sessions.config_dir == Path("explicit/sessions")


def test_app_settings_with_missing_json_file():
    """Test that AppSettings works when configs/settings.json is missing."""
    # Temporarily rename the settings file
    settings_file = Path("configs/settings.json")
    backup_file = Path("configs/settings.json.backup")
    
    if settings_file.exists():
        settings_file.rename(backup_file)
    
    try:
        # Should still work with defaults
        settings = AppSettings()
        # Test that the object can be created and has the expected structure
        assert hasattr(settings, 'logging')
        assert hasattr(settings, 'portfolio')
        assert hasattr(settings, 'sessions')
        assert settings.portfolio.config_dir == Path("configs/portfolios")  # Default value
        assert settings.sessions.config_dir == Path("configs/sessions")  # Default value
    finally:
        # Restore the file
        if backup_file.exists():
            backup_file.rename(settings_file)


def test_app_settings_nested_configuration():
    """Test that AppSettings properly handles nested configuration."""
    config_dict = {
        "logging": {
            "config_path": "custom/logging.json"
        },
        "portfolio": {
            "config_dir": "nested/portfolios"
        },
        "sessions": {
            "config_dir": "nested/sessions"
        }
    }

    settings = AppSettings(**config_dict)

    # Verify nested configuration is properly loaded
    assert settings.logging.config_path == Path("custom/logging.json")
    assert settings.portfolio.config_dir == Path("nested/portfolios")
    assert settings.sessions.config_dir == Path("nested/sessions")


def test_app_settings_partial_override():
    """Test that AppSettings allows partial overrides."""
    # Only override portfolio, leave others as defaults
    config_dict = {
        "portfolio": {
            "config_dir": "partial/portfolios"
        }
    }

    settings = AppSettings(**config_dict)

    # Portfolio should be overridden
    assert settings.portfolio.config_dir == Path("partial/portfolios")
    # Others should use defaults from JSON file
    assert settings.sessions.config_dir == Path("configs/sessions")
    assert settings.logging.config_path == Path("configs/logging.json")


def test_app_settings_creates_valid_objects():
    """Test that AppSettings creates valid objects with expected structure."""
    settings = AppSettings()
    
    # Test that all expected attributes exist
    assert hasattr(settings, 'logging')
    assert hasattr(settings, 'portfolio')
    assert hasattr(settings, 'sessions')
    
    # Test that nested objects have expected attributes
    assert hasattr(settings.logging, 'config_path')
    assert hasattr(settings.portfolio, 'config_dir')
    assert hasattr(settings.sessions, 'config_dir')
    
    # Test that values are of expected types
    assert isinstance(settings.logging.config_path, (Path, type(None)))
    assert isinstance(settings.portfolio.config_dir, Path)
    assert isinstance(settings.sessions.config_dir, Path)




