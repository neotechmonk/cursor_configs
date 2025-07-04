from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

from core.portfolio.portfolio import PortfolioSettings


class AppSettings(BaseSettings):
    """Global application settings with domain sections."""
    model_config = ConfigDict(
        json_file="configs/settings.json",
        json_file_encoding="utf-8",
    )
    
    portfolio: PortfolioSettings = Field(
        default_factory=PortfolioSettings
    )