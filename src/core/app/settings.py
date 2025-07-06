from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

from core.portfolio.portfolio import PortfolioSettings
from core.sessions.session import TradingSessionSettings


class AppSettings(BaseSettings):
    """Global application settings with domain sections."""
    model_config = ConfigDict(
        json_file="configs/settings.json",
        json_file_encoding="utf-8",
    )
    
    portfolio: PortfolioSettings = Field(
        default_factory=PortfolioSettings
    )

    sessions: TradingSessionSettings = Field(
        default_factory=TradingSessionSettings
    )