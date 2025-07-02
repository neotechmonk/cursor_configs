"""Price feeds container for managing price feed providers."""

from pathlib import Path
from typing import Dict

from dependency_injector import containers, providers

from ..feed.protocols import PriceFeedProvider
from ..loaders.load_providers import get_available_providers, load_provider



def _load_all_providers(providers_dir: Path) -> Dict[str, PriceFeedProvider]:
    """Load all available providers from YAML files.
    
    Args:
        providers_dir: Directory containing provider YAML files
        
    Returns:
        Dictionary mapping provider names to provider instances
    """
    providers = {}
    
    # Get all YAML files in providers directory
    for config_file in providers_dir.glob("*.yaml"):
        provider_name = config_file.stem  # filename without extension
        
        if provider_name in get_available_providers():
            try:
                providers[provider_name] = load_provider(providers_dir, provider_name)
            except Exception as e:
                # Log error but continue loading other providers
                print(f"Failed to load provider {provider_name}: {e}")
    
    return providers


class PriceFeedsContainer(containers.DeclarativeContainer):
    """Container for managing price feed providers.
    
    This container provides dynamic loading of price feed providers from YAML files.
    Providers are loaded based on available YAML files in the providers directory.
    
    Configuration:
        providers_dir: Path to the directory containing provider YAML files.
                       Defaults to ./configs/providers/
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Dependencies
    providers_dir = providers.Dependency(
        instance_of=Path
    )
    
    # Dynamic provider loader
    provider = providers.Factory(
        load_provider,
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
        super().wire(*args, **kwargs)
        
        # Validate providers_dir is provided and valid
        if not self.providers_dir.provided:
            raise ValueError("providers_dir is required but not provided")
            
        if not isinstance(self.providers_dir(), Path):
            raise ValueError("providers_dir must be a Path object")
            
        if not self.providers_dir().exists():
            raise ValueError(f"Providers directory does not exist: {self.providers_dir()}")
