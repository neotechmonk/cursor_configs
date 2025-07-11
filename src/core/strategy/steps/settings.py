from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class StrategyStepSettings(BaseSettings):
    """Strategy step-specific settings from app configuration."""
    config_path: Path = Field(default=Path("configs/strategies/_steps/strategy_steps.yaml"))
