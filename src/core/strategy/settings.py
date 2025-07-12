from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from core.strategy.steps.settings import StrategyStepSettings


class StrategySettings(BaseSettings):
    """Strategy-specific settings from app configuration."""
    config_dir: Path = Field(default=Path("configs/strategies"))
    steps_settings: StrategyStepSettings 
    