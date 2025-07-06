import json
import tempfile
from pathlib import Path

import pytest

from src.core.app.settings import AppSettings


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


def test_app_settings_loads_from_json(temp_settings_file):
    with open(temp_settings_file, "r", encoding="utf-8") as f:
        config_dict = json.load(f)

    settings = AppSettings(**config_dict)
    assert settings.portfolio.config_dir == Path("json/portfolios")


def test_app_settings_defaults():
    """Test that AppSettings uses defaults when no JSON file."""
    settings = AppSettings()
    assert settings.portfolio.config_dir == Path("configs/portfolios")
    assert settings.sessions.config_dir == Path("configs/sessions")


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

    settings =AppSettings(**config_dict)
    assert settings.portfolio.config_dir == Path("dict/portfolios")
    assert settings.sessions.config_dir == Path("dict/sessions")



