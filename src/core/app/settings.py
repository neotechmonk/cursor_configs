import json
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.app.logging import LoggingSettings
from core.portfolio.portfolio import PortfolioSettings
from core.sessions.session import TradingSessionSettings


def custom_settings_source(settings: BaseSettings = None) -> dict[str, Any]:
    """Read additional settings from a custom JSON file.
    
    This function is used by BaseSettings to load configuration from configs/settings.json.
    """
    json_file = Path("configs/settings.json")
    
    if json_file.exists():
        try:
            with open(json_file, "r", encoding="utf-8") as config_file:
                return json.load(config_file)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not load settings from {json_file}: {e}")
    
    return {}


class AppSettings(BaseSettings):
    """Global application settings with domain sections.
    
    This class loads configuration from multiple sources in order of priority:
    1. Explicitly passed settings (highest priority)
    2. Environment variables
    3. .env file
    4. configs/settings.json (via custom_settings_source)
    5. Secrets directory (lowest priority)
    """
    
    # Domain-specific settings
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    portfolio: PortfolioSettings = Field(default_factory=PortfolioSettings)
    sessions: TradingSessionSettings = Field(default_factory=TradingSessionSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="allow"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        cls_type,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Customize the order of configuration sources.
        
        This method defines the priority order for loading settings:
        1. Explicitly passed settings (highest priority)
        2. Environment variables
        3. .env file
        4. Custom JSON file (configs/settings.json)
        5. Secrets directory (lowest priority)
        """
        return (
            init_settings,           # First, use explicitly passed settings (highest priority)
            env_settings,            # Then, read from environment variables
            dotenv_settings,         # Then, read from .env file
            file_secret_settings,    # Then, read from the secrets directory (lowest priority)
            custom_settings_source,  # Finally, read from the custom JSON file
        )