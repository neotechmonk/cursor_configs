"""Root container for managing all dependencies."""

from dependency_injector import containers, providers

from .price_provider import PriceFeedsContainer
from .steps import StepRegistryContainer
from .strategies import StrategiesContainer


class RootContainer(containers.DeclarativeContainer):
    """Root container that manages all dependencies.
    
    This container combines the step registry, strategy, and price feeds containers,
    providing the step registry to the strategy container and price feeds to trading sessions.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Step registry container
    steps = providers.Container(
        StepRegistryContainer,
        config=config.step_registry,
        registry_file=config.step_registry.registry_file
    )
    
    # Strategy container
    strategies = providers.Container(
        StrategiesContainer,
        config=config,
        step_registry=steps.registry,
        strategies_dir=config.strategies.dir
    )
    
    # Price feeds container
    price_feeds = providers.Container(
        PriceFeedsContainer,
        config=config.price_feeds,
        providers_dir=config.price_feeds.providers_dir
    )

    