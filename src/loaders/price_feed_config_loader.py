"""Loader for price feed configuration."""

from pathlib import Path
from typing import Dict, Optional, Type

import yaml

from core.feed import (
    CSVPriceFeedConfig,
    CSVPriceFeedProvider,
    PriceFeedConfig,
    YahooFinanceConfig,
    YahooFinanceProvider,
)
from core.protocols import PriceFeedProvider


class PriceFeedProviderFactory:
    """Factory for creating price feed providers."""
    
    _provider_classes: Dict[str, Type[PriceFeedProvider]] = {
        "yahoo": YahooFinanceProvider,
        "csv": CSVPriceFeedProvider,
    }
    
    @classmethod
    def create_provider(cls, config: PriceFeedConfig) -> PriceFeedProvider:
        """Create a price feed provider from its configuration.
        
        Args:
            config: Provider configuration
            
        Returns:
            Price feed provider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        provider_class = cls._provider_classes.get(config.name)
        if not provider_class:
            raise ValueError(f"Unsupported provider type: {config.name}")
        return provider_class(config)


class PriceFeedConfigLoader:
    """Loader for price feed configuration."""
    
    def __init__(self, config_path: Path):
        """Initialize the loader.
        
        Args:
            config_path: Path to configuration file
        """
        self._config_path = config_path
        self._configs: Dict[str, PriceFeedConfig] = {}
        self._load_configs()
    
    def _load_configs(self) -> None:
        """Load configurations from file."""
        with open(self._config_path) as f:
            config_data = yaml.safe_load(f)
        
        for name, data in config_data.items():
            if name == "yahoo":
                self._configs[name] = YahooFinanceConfig(**data)
            elif name == "csv":
                self._configs[name] = CSVPriceFeedConfig(**data)
            else:
                raise ValueError(f"Unsupported provider type: {name}")
    
    def get_provider_config(self, name: str) -> Optional[PriceFeedConfig]:
        """Get provider configuration by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider configuration if found, None otherwise
        """
        return self._configs.get(name)
    
    def create_provider(self, name: str) -> Optional[PriceFeedProvider]:
        """Create a provider instance by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance if configuration found, None otherwise
        """
        config = self.get_provider_config(name)
        if not config:
            return None
        return PriceFeedProviderFactory.create_provider(config) 