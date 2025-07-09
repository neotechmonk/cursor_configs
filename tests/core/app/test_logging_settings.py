import json
import tempfile
from pathlib import Path

from core.app.settings import LoggingSettings


def test_logging_settings_defaults():
    """Test LoggingSettings defaults without config_path."""
    settings = LoggingSettings()
    assert settings.level == "WARN"
    assert settings.config_path is None
    assert settings.dict_config is None


def test_logging_settings_from_config_path():
    """Test LoggingSettings loads values from a valid JSON config."""
    json_config = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(levelname)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG"
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"]
        }
    }

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        json.dump(json_config, tmp)
        tmp_path = Path(tmp.name)

    settings = LoggingSettings(config_path=Path(tmp_path))

    assert settings.level == "DEBUG"
    assert settings.format == "%(levelname)s: %(message)s"
    assert settings.config_path == tmp_path
    assert settings.dict_config is not None
    assert settings.dict_config["root"]["level"] == "DEBUG"

    tmp_path.unlink()  # Clean up