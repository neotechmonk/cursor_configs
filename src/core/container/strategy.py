"""Strategy container for managing trading strategies."""

from pathlib import Path

from dependency_injector import containers, providers

from src.core.strategy_loader import StrategyLoader


class StrategyContainer(containers.DeclarativeContainer):
    """Container for managing trading strategies.
    
    This container provides access to configured strategies and their execution.
    Strategies are loaded dynamically from the configs/strategies directory.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Dependencies
    step_registry = providers.Dependency()
    
    # Strategy loader
    strategy_loader = providers.Factory(
        StrategyLoader,
        registry=step_registry
    )
    
    # Strategy registry (available strategies)
    strategy_registry = providers.Singleton(
        lambda: {
            path.stem: path 
            for path in Path(config.strategies_dir).glob("*.yaml")
        }
    )
    
    # Available strategy names
    available_strategies = providers.Factory(
        lambda: list(strategy_registry().keys())
    )
    
    # Dynamic strategy loader
    strategy = providers.Factory(
        lambda name: strategy_loader().load_strategy(
            name,
            config_dir=config.strategies_dir
        )
    ) 