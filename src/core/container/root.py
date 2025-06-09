"""Root container for managing all dependencies."""

from dependency_injector import containers, providers

from .steps import StepRegistryContainer
from .strategies import StrategiesContainer


class RootContainer(containers.DeclarativeContainer):
    """Root container that manages all dependencies.
    
    This container combines the step registry and strategy containers,
    providing the step registry to the strategy container.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Step registry container
    steps = providers.Container(
        StepRegistryContainer,
        config=config.step_registry
    )
    
    # Strategy container
    strategies = providers.Container(
        StrategiesContainer,
        config=config.strategies,
        step_registry=steps.registry
    )

    wiring_config = containers.WiringConfiguration(
    modules=[
        "main",  # entry point module
        # add other modules needing @inject or Provide[] here
    ]
) 