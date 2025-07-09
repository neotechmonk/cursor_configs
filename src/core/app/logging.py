import json
import logging.config
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, model_validator


class LoggingSettings(BaseModel):
    #Defaults 
    level: Literal["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"] = "WARN"
    format: str = "%(asctime)s - %(levelname)s - %(message)s"

    #Configurable overrides
    config_path: Optional[Path] = None
    dict_config: Optional[dict[str, Any]] = None

    @model_validator(mode="after")
    def load_from_file(self) -> "LoggingSettings":
        if self.config_path and self.config_path.exists():
            loaded_dict = json.loads(self.config_path.read_text())
            self.dict_config = loaded_dict


            # Update the default attributes
            self.level = loaded_dict.get("root", {}).get("level", self.level)
            self.format = loaded_dict.get("formatters", {}).get("default", {}).get("format", self.format)
        return self


def configure_logging(settings: LoggingSettings):
    if settings.dict_config:
        logging.config.dictConfig(settings.dict_config)
    else:
        logging.basicConfig(level="INFO")  # fallback if no config