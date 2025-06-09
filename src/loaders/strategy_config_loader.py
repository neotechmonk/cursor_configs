"""Loader for strategy configurations."""

from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import ValidationError

from src.models.strategy import StrategyConfig, StrategyStep
from src.models.system import StrategyStepRegistry


class StrategyConfigLoader:
    """Loader for strategy configurations from YAML files."""
    
    def __init__(
        self,
        config_dir: Path = Path("configs/strategies"),
        step_registry: Optional[StrategyStepRegistry] = None
    ):
        """Initialize the strategy config loader.
        
        Args:
            config_dir: Directory containing strategy YAML files
            step_registry: Registry to resolve step templates
        """
        self.config_dir = config_dir
        self.step_registry = step_registry
        
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Strategy config directory not found: {self.config_dir}")
    
    def load_all_strategies(self) -> Dict[str, StrategyConfig]:
        """Load all strategy configurations from YAML files.
        
        Returns:
            Dictionary mapping strategy names to their configurations
            
        Raises:
            yaml.YAMLError: If any YAML file is invalid
            ValidationError: If any strategy config is invalid
        """
        strategies = {}
        for yaml_file in self.config_dir.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            try:
                strategy = self.create_strategy(data)
                strategies[strategy.name] = strategy
            except ValidationError as e:
                # Add file context to the error message
                e.add_note(f"Invalid strategy config in {yaml_file}")
                raise
                
        return strategies
    
    def load_strategy(self, name: str) -> StrategyConfig:
        """Load a specific strategy configuration by name.
        
        Args:
            name: Name of the strategy to load
            
        Returns:
            StrategyConfig object
            
        Raises:
            FileNotFoundError: If no strategy config with given name exists
            yaml.YAMLError: If YAML file is invalid
            ValidationError: If strategy config is invalid
        """
        yaml_file = self.config_dir / f"{name}.yaml"
        if not yaml_file.exists():
            raise FileNotFoundError(f"No strategy config found for: {name}")
            
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            
        try:
            return self.create_strategy(data)
        except ValidationError as e:
            e.add_note(f"Invalid strategy config in {yaml_file}")
            raise
    
    def _resolve_reevaluates(self, step: StrategyStep, step_data: dict, step_map: Dict[str, StrategyStep]) -> None:
        """Resolve reevaluation step references to actual StrategyStep objects.
        
        Args:
            step: The step whose reevaluates need to be resolved
            step_data: The raw step data from the YAML
            step_map: Map of system_step_id to StrategyStep objects
            
        Raises:
            ValueError: If a referenced step is not found
        """
        if 'reevaluates' in step_data:
            reevaluates = []
            for step_id in step_data['reevaluates']:
                if step_id not in step_map:
                    raise ValueError(f"Reevaluation step '{step_id}' not found in strategy")
                reevaluates.append(step_map[step_id])
            step.reevaluates = reevaluates

    def create_strategy(self, data: dict) -> StrategyConfig:
        """Create a StrategyConfig from data.
        
        Args:
            data: Dictionary containing strategy configuration
            
        Returns:
            StrategyConfig object
            
        Raises:
            ValidationError: If strategy data is invalid
        """
        # First pass: Create all StrategyStep objects and track reevaluation relationships
        steps = []
        step_map = {}  # Map system_step_id to StrategyStep
        reevaluation_map = {}  # Map step_id to list of steps that need to be reevaluated
        
        for step_data in data['steps']:
            # Store reevaluates and remove from step_data before creating step
            reevaluation_map[step_data['system_step_id']] = step_data.pop('reevaluates', [])
            
            # Create step without reevaluates
            template = self.step_registry.get_step_template(step_data['system_step_id'])
            step = StrategyStep(template=template, **step_data)
            
            # Store step
            steps.append(step)
            step_map[step.system_step_id] = step
            
        # Second pass: Apply all reevaluation relationships at once
        for step_id, reevaluates_ids in reevaluation_map.items():
            step_map[step_id].reevaluates = [
                step_map[ref_id] for ref_id in reevaluates_ids
                if ref_id in step_map
            ]
            
        # Create strategy config
        return StrategyConfig(name=data['name'], steps=steps)


# For backward compatibility
def create_strategy(data: dict, step_registry: StrategyStepRegistry) -> StrategyConfig:
    """Create a StrategyConfig from data and registry.
    
    Args:
        data: Dictionary containing strategy configuration
        step_registry: Registry to resolve step templates
        
    Returns:
        StrategyConfig object
        
    Raises:
        ValidationError: If strategy data is invalid
    """
    loader = StrategyConfigLoader(step_registry=step_registry)
    return loader.create_strategy(data)


def load_strategy_configs(
    config_dir: Path = Path("configs/strategies"),
    step_registry: Optional[StrategyStepRegistry] = None
) -> Dict[str, StrategyConfig]:
    """Load all strategy configurations from YAML files.
    
    Args:
        config_dir: Directory containing strategy YAML files
        step_registry: Optional registry to resolve step templates
        
    Returns:
        Dictionary mapping strategy names to their configurations
        
    Raises:
        FileNotFoundError: If config_dir doesn't exist
        yaml.YAMLError: If any YAML file is invalid
        ValidationError: If any strategy config is invalid
    """
    loader = StrategyConfigLoader(config_dir=config_dir, step_registry=step_registry)
    return loader.load_all_strategies() 