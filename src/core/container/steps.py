"""Step registry container for managing strategy step templates."""

from pathlib import Path

from dependency_injector import containers, providers

from src.models.system import StrategyStepRegistry


class StepRegistryContainer(containers.DeclarativeContainer):
    """Container for managing strategy step templates.
    
    This container provides access to the strategy step registry, which contains
    all available step templates that can be used in strategies.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Dependencies
    registry_file = providers.Dependency(
        instance_of=Path
    )
    
    # Registry singleton
    registry = providers.Singleton(
        StrategyStepRegistry.from_yaml,
        yaml_file=registry_file
    )
    
    def wire(self, *args, **kwargs) -> None:
        """Wire the container and validate configuration."""
        super().wire(*args, **kwargs)
        
        # Validate registry_file is provided and valid
        if not self.registry_file.provided:
            raise ValueError("registry_file is required but not provided")
            
        if not isinstance(self.registry_file(), Path):
            raise ValueError("registry_file must be a Path object")
            
        if not self.registry_file().exists():
            raise ValueError(f"Registry file does not exist: {self.registry_file()}") 