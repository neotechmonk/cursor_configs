from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class LoggingSettings(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(levelname)s - %(message)s"
    config_path: Optional[Path] = None
