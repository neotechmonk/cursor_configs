# src/core/container/price_feeds.py
"""Price feeds container for managing price feed providers."""

from pathlib import Path
from typing import Dict

from dependency_injector import containers, providers

# Import provider classes
from core.feed.providers.csv_file import CSVPriceFeedConfig, CSVPriceFeedProvider
from src.core.feed.protocols import PriceFeedProvider

# from src.core.feed.providers.yahoo import YahooFinanceConfig, YahooFinanceProvider
from src.loaders.generic import load_yaml_config
from utils import deprecated

# Provider mapping - easy to update when adding new providers
PROVIDERS = {
    "csv": (CSVPriceFeedProvider, CSVPriceFeedConfig),
    # "yahoo": (YahooFinanceProvider, YahooFinanceConfig),
}


def _validate_providers_dir(providers_dir) -> Path:
    """Validate that providers_dir is a Path object."""
    if not isinstance(providers_dir, Path):
        raise ValueError(f"{providers_dir} is not an instance of <class 'pathlib.Path'>")
    return providers_dir


def _create_provider_by_name(providers_dir: Path, name: str) -> PriceFeedProvider:
    """Create provider using filename to infer provider type."""
    # Validate providers_dir type
    providers_dir = _validate_providers_dir(providers_dir)
    
    config_path = providers_dir / f"{name}.yaml"
    
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}")
    
    provider_class, config_class = PROVIDERS[name]
    
    # Use generic loader
    config = load_yaml_config(config_path, config_class)
    return provider_class(config)


def _load_all_providers(providers_dir: Path) -> Dict[str, PriceFeedProvider]:
    """Load all available providers from YAML files."""
    # Validate providers_dir type
    providers_dir = _validate_providers_dir(providers_dir)
    
    if not providers_dir.exists():
        raise FileNotFoundError(f"Providers directory not found: {providers_dir}")
    
    providers = {}
    
    for config_file in providers_dir.glob("*.yaml"):
        provider_name = config_file.stem
        try:
            providers[provider_name] = _create_provider_by_name(providers_dir, provider_name)
        except Exception as e:
            print(f"Failed to load provider {provider_name}: {e}")
    
    return providers


class PriceFeedsContainer(containers.DeclarativeContainer):
    """Container for managing price feed providers."""
    
    # Configuration
    config = providers.Configuration()
    
    # Dependencies - remove instance_of since it's not working as expected
    providers_dir = providers.Dependency(instance_of=Path, default=Path("configs/providers"))
    
    # Provider factory
    @deprecated("Use get() instead")
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
        lambda providers: list(providers.keys()),
        all_providers
    )
    
    def wire(self, *args, **kwargs) -> None:
        """Wire the container and validate configuration."""
        print("DEBUG: wire() method called")
        super().wire(*args, **kwargs)
        
        print(f"DEBUG: providers_dir = {self.providers_dir()}")
        print(f"DEBUG: providers_dir exists = {self.providers_dir().exists()}")
        
        if not self.providers_dir().exists():
            print("DEBUG: About to raise ValueError")
            raise ValueError(f"Providers directory does not exist: {self.providers_dir()}")