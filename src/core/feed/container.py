# src/core/container/price_feeds.py
"""Price feeds container for managing price feed providers."""

from pathlib import Path
from typing import Dict, List

from dependency_injector import containers, providers

from core.feed.protocols import PriceFeedProvider

# Import provider classes
from core.feed.providers.csv import CSVPriceFeedConfig, CSVPriceFeedProvider

# from core.feed.providers.yahoo import YahooFinanceConfig, YahooFinanceProvider
from loaders.generic import load_yaml_config

# Provider mapping - easy to update when adding new providers
PROVIDERS = {
    "csv": (CSVPriceFeedProvider, CSVPriceFeedConfig),
    # "yahoo": (YahooFinanceProvider, YahooFinanceConfig),
}


def _create_provider_by_name(providers_dir: Path, name: str) -> PriceFeedProvider:
    """Create provider using filename to infer provider type."""
    
    config_path = providers_dir / f"{name}.yaml"
    
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}")
    
    provider_class, config_class = PROVIDERS[name]
    
    config = load_yaml_config(config_path, config_class)
    return provider_class(config)


def _load_all_providers(providers_dir: Path) -> Dict[str, PriceFeedProvider]:
    """Load all available providers from YAML files."""
    
    providers = {}
    
    for config_file in providers_dir.glob("*.yaml"):
        provider_name = config_file.stem
        try:
            providers[provider_name] = _create_provider_by_name(providers_dir, provider_name)
        except Exception as e:
            print(f"Failed to load provider {provider_name}: {e}")
    
    return providers


def _get_available_providers(providers_dir: Path) -> List[str]:
    """Get list of available provider names."""
    available = []
    for config_file in providers_dir.glob("*.yaml"):
        provider_name = config_file.stem
        if provider_name in PROVIDERS:
            available.append(provider_name)
    return available


class PriceFeedsContainer(containers.DeclarativeContainer):
    """Container for managing price feed providers."""
    
    # Configuration
    config = providers.Configuration()
    
    # Dependencies - remove instance_of since it's not working as expected
    providers_dir = providers.Dependency(instance_of=Path, default=Path("configs/providers"))
    
    # Provider factory
    provider = providers.Factory(
        _create_provider_by_name,
        providers_dir=providers_dir,
        name=providers.Dependency()
    )
    
    # All providers (loaded dynamically)
    all_providers = providers.Singleton(
        _load_all_providers,
        providers_dir=providers_dir
    )
    
    # Available provider names
    available_providers = providers.Singleton(
        _get_available_providers,
        providers_dir=providers_dir
    )
    
    def wire(self, *args, **kwargs) -> None:
        """Wire the container and validate configuration."""
        super().wire(*args, **kwargs)

        if not isinstance(self.providers_dir(), Path):
            raise ValueError(f"{self.providers_dir()} is not an instance of <class 'pathlib.Path'>")
    
        if not self.providers_dir().exists():
            raise ValueError(f"Providers directory does not exist: {self.providers_dir()}")