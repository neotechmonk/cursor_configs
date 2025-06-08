"""Strategy container for managing trading strategies."""

from pathlib import Path
from typing import Dict, List, Optional

from dependency_injector import containers, providers

from src.loaders.strategy_config_loader import create_strategy, load_strategy_configs
from src.models.strategy import StrategyConfig
from src.models.system import StrategyStepRegistry


class StrategyContainer(containers.DeclarativeContainer):
    """Strategy container for managing trading strategies.
    
    This container provides access to configured strategies and their execution.
    Strategies are loaded dynamically from the configs/strategies directory.
    
    Requires:
        step_registry: StrategyStepRegistry instance for validating strategy steps
        
    Configuration:
        strategies_dir: Path to the directory containing strategy YAML files.
                       Defaults to ./configs/strategies/
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Default configuration values
    config.strategies_dir.from_value(
        Path(__file__).parent.parent.parent.parent / "configs" / "strategies"
    )
    
    # Dependencies - step_registry is required
    step_registry = providers.Dependency(
        instance_of=StrategyStepRegistry
    )
    
    # Loaded strategies
    strategies = providers.Singleton(
        lambda config_dir, registry: load_strategy_configs(config_dir, registry),
        config.strategies_dir,
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
    
    def wire(self, *args, **kwargs) -> None:
        """Wire the container and validate configuration."""
        super().wire(*args, **kwargs)
        
        # Validate config directory exists
        config_dir = Path(self.config.strategies_dir())
        if not config_dir.exists():
            raise ValueError(f"Strategies directory does not exist: {config_dir}")
            
        # Validate step registry is provided and valid
        if not self.step_registry.provided:
            raise ValueError("step_registry is required but not provided")
            
        if not isinstance(self.step_registry(), StrategyStepRegistry):
            raise ValueError("step_registry must be an instance of StrategyStepRegistry") 