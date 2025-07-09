import logging
from pathlib import Path

import pytest

from core.app.container import AppContainer


@pytest.fixture
def logging_config_file(tmp_path: Path) -> Path:
    """Create a sample logging config file."""
    logging_path = tmp_path / "konfigs" / "logging.json"
    logging_path.parent.mkdir(parents=True, exist_ok=True)
    logging_path.write_text('''
    {
        "version": 1,
        "disable_existing_loggers": false,
        "formatters": {
            "default": {
                "format": "%(levelname)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }
    ''')
    return logging_path


@pytest.fixture
def settings_config_file(tmp_path: Path, logging_config_file: Path) -> Path:
    """Create a sample AppSettings config file that points to the logging config."""
    config_path = logging_config_file.relative_to(tmp_path)
    settings_path = tmp_path / "configs" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(f'''
    {{
        "logging": {{
            "config_path": "{config_path.as_posix()}"
        }},
        "portfolio": {{
            "config_dir": "konfigs/portfolios"
        }},
        "sessions": {{
            "config_dir": "konfigs/sessions"
        }}
    }}
    ''')
    return settings_path


def test_app_container_initialises_logger(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, settings_config_file: Path):
    """Test that AppContainer initialises logging using config path and returns logger instance."""
    monkeypatch.setenv("APP_SETTINGS_PATH", str(settings_config_file))

    # Instantiate and initialise
    container = AppContainer()
    container.init_resources()

    # Ensure logger is available
    logger = container.logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "core"
    logger.debug(f"Logger initialised successfully at level {logger}")

    # Check config values were loaded
    settings = container.settings()
    assert settings.logging.config_path == Path("konfigs/logging.json")
    assert settings.portfolio.config_dir == Path("konfigs/portfolios")
    assert settings.sessions.config_dir == Path("konfigs/sessions")