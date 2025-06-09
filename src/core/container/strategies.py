"""Strategy container for managing trading strategies."""

from pathlib import Path

from dependency_injector import containers, providers

from src.loaders.strategy_config_loader import load_strategy_configs
from src.models.system import StrategyStepRegistry


class StrategiesContainer(containers.DeclarativeContainer):
    """Strategy container for managing trading strategies.
    
    This container provides access to configured strategies and their execution.
    Strategies are loaded dynamically from the configs/strategies directory.
    
    Requires:
        step_registry: StrategyStepRegistry instance for validating strategy steps
        
    Configuration:
        strategies.dir: Path to the directory containing strategy YAML files.
                       Defaults to ./configs/strategies/
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Dependencies
    step_registry = providers.Dependency(
        instance_of=StrategyStepRegistry
    )
    
    strategies_dir = providers.Dependency(
        instance_of=Path
    )
    
    # Loaded strategies
    strategies = providers.Singleton(
        lambda config_dir, registry: load_strategy_configs(config_dir, registry),
        strategies_dir,
        step_registry
    )
    
    # Available strategy names
    available_strategies = providers.Singleton(
        lambda strategies: list(strategies.keys()),
        strategies
    )
    
    # Dynamic strategy loader with caching
    strategy = providers.Factory(
        lambda strategies, name: strategies.get(name),
        strategies
    )
    
    # Strategy reloader
    reload_strategies = providers.Factory(
        lambda config_dir, registry: load_strategy_configs(config_dir, registry),
        strategies_dir,
        step_registry
    )
    
    # Strategy validator (reloads and validates a single strategy by name)
    validate_strategy = providers.Factory(
        lambda config_dir, registry, name: load_strategy_configs(config_dir, registry)[name],
        strategies_dir,
        step_registry
    )
    
    def wire(self, *args, **kwargs) -> None:
        """Wire the container and validate configuration."""
        super().wire(*args, **kwargs)
        
        # Validate strategies_dir is provided and valid
        if not self.strategies_dir.provided:
            raise ValueError("strategies_dir is required but not provided")
            
        if not isinstance(self.strategies_dir(), Path):
            raise ValueError("strategies_dir must be a Path object")
            
        if not self.strategies_dir().exists():
            raise ValueError(f"Strategies directory does not exist: {self.strategies_dir()}")
            
        # Validate step registry is provided and valid
        if not self.step_registry.provided:
            raise ValueError("step_registry is required but not provided")
            
        if not isinstance(self.step_registry(), StrategyStepRegistry):
            raise ValueError("step_registry must be an instance of StrategyStepRegistry") 