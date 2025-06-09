"""Step registry container for managing strategy step templates."""

from dependency_injector import containers, providers

from src.models.system import StrategyStepRegistry


class StepRegistryContainer(containers.DeclarativeContainer):
    """Container for managing strategy step templates.
    
    This container provides access to the strategy step registry, which contains
    all available step templates that can be used in strategies.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Registry singleton
    registry = providers.Singleton(
        StrategyStepRegistry.from_yaml,
        yaml_file=config.registry_file
    ) 