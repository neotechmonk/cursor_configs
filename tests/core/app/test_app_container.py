import os
import logging
from pathlib import Path
from textwrap import dedent

import pytest

from core.app.container import AppContainer
from core.app.settings import AppSettings


@pytest.fixture
def temporary_root_dir(tmp_path: Path) -> Path:
    """Create a temporary root directory for the test."""
    return tmp_path


@pytest.fixture
def logging_config_file(temporary_root_dir: Path) -> Path:
    """Create a sample logging config file."""
    logging_path = temporary_root_dir / "konfigs" / "logging.json"
    logging_path.parent.mkdir(parents=True, exist_ok=True)
    logging_path.write_text(dedent('''\
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
    '''))
    return logging_path


@pytest.fixture
def strategy_steps_file(temporary_root_dir: Path) -> Path:
    """Create a dummy strategy steps YAML config file."""
    steps_path = temporary_root_dir / "configs" / "strategies" / "_steps" / "strategy_steps.yaml"
    steps_path.parent.mkdir(parents=True, exist_ok=True)
    steps_path.write_text(dedent('''\
        - id: dummy_id
          name: dummy
          type: example_step
          function_path: dummy_module.dummy_function
          params: {}
    '''))
    return steps_path


@pytest.fixture
def settings_config_file(
    temporary_root_dir: Path,
    logging_config_file: Path,
    strategy_steps_file: Path
) -> Path:
    """Create a sample AppSettings config file that points to logging and steps configs."""
    logging_rel = logging_config_file.relative_to(temporary_root_dir)
    steps_rel = strategy_steps_file.relative_to(temporary_root_dir)

    settings_path = temporary_root_dir / "configs" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings_path.write_text(dedent(f'''\
        {{
            "logging": {{
                "config_path": "{logging_rel.as_posix()}"
            }},
            "portfolio": {{
                "config_dir": "konfigs/portfolios"
            }},
            "sessions": {{
                "config_dir": "konfigs/sessions"
            }},
            "strategy": {{
                "config_dir": "configs/strategies",
                "steps_settings": {{
                    "config_path": "{steps_rel.as_posix()}"
                }}
            }}
        }}
    '''))
    return settings_path

# @pytest.mark.skip(reason="Cause side effects for other tests")
def test_app_container_initialises_logger(
    settings_config_file: Path,
    temporary_root_dir: Path, 
    monkeypatch: pytest.MonkeyPatch
):
    """Test that AppContainer initialises logging using config path and returns logger instance."""
    # Set the settings path to the environment variable
    monkeypatch.setenv("APP_SETTINGS_PATH", str(settings_config_file))

    # Set current directory to root dir to support relative paths inside container logic
    # os.chdir(temporary_root_dir)
    monkeypatch.chdir(temporary_root_dir)  # noqa: F821

    # Instantiate and initialise the container
    container = AppContainer()
    container.settings.override(AppSettings(config_path=settings_config_file))
    container.init_resources()

    # Ensure logger is available
    logger = container.logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "core"

    # Ensure settings were loaded correctly
    settings = container.settings()
    assert settings.logging.config_path == Path("konfigs/logging.json")
    assert settings.portfolio.config_dir == Path("konfigs/portfolios")
    assert settings.sessions.config_dir == Path("konfigs/sessions")
    assert settings.strategy.config_dir == Path("configs/strategies")
    assert settings.strategy.steps_settings.config_path == Path("configs/strategies/_steps/strategy_steps.yaml")

    