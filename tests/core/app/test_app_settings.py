import json
import tempfile
from pathlib import Path

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


# @pytest.mark.skip()
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



def test_app_settings_loads_from_json(temp_settings_file):
    """Test that AppSettings can load from a custom JSON file."""
    with open(temp_settings_file, "r", encoding="utf-8") as f:
        config_dict = json.load(f)

    settings = AppSettings(**config_dict)
    assert settings.portfolio.config_dir == Path("json/portfolios")


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



