import json
import logging.config
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, model_validator


class LoggingSettings(BaseModel):
    config_path: Optional[Path] = None

def load_logging_config(config_path: Path) -> None:
    """
    Load and apply logging configuration from a JSON file if the file exists and is valid.

    Parameters:
        config_path (Path): Path to the logging configuration JSON file.
    """
    if not config_path or not config_path.exists():
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).warning(f"No logging config found at {config_path}. Using default config.")
        return

    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as e:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).exception(f"Failed to load logging config from {config_path}. Using default config. Error: {e}")