"""Loader for strategy configurations."""

from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import ValidationError

from models.strategy import StrategyConfig, StrategyStep
from models.system import StrategyStepRegistry


def create_new_strategy(strategy_data: dict, step_registry: StrategyStepRegistry) -> StrategyConfig:
        """Create a StrategyConfig from strategy data.
        
        Args:
            strategy_data: Dictionary containing strategy configuration with 'name' and 'steps'
            step_registry: Registry to resolve step templates
            
        Returns:
            StrategyConfig object
            
        Raises:
            ValidationError: If strategy data is invalid
        """
        steps = []
        step_map = {}  # Map system_step_id to StrategyStep
        
        for step_data in strategy_data['steps']:
            # Get reevaluates before creating step
            reevaluates_ids = step_data.pop('reevaluates', [])
            
            # Create step without reevaluates
            template = step_registry.get_step_template(step_data['system_step_id'])
            new_step = StrategyStep(template=template, **step_data)
            
            # Store step
            steps.append(new_step)
            step_map[new_step.system_step_id] = new_step
            
            # Resolve reevaluates immediately using steps we've created so far
            new_step.reevaluates = [
                step_map[ref_id] for ref_id in reevaluates_ids
                if ref_id in step_map
            ]
            
        # Create strategy config
        return StrategyConfig(name=strategy_data['name'], steps=steps)


def load_strategies(
    strategies_dir: Path = Path("configs/strategies"),
    step_registry: Optional[StrategyStepRegistry] = None
) -> Dict[str, StrategyConfig]:
    """Load all strategy configurations from YAML files.
    
    Args:
        strategies_dir: Directory containing strategy YAML files
        step_registry: Optional registry to resolve step templates
        
    Returns:
        Dictionary mapping strategy names to their configurations
        
    Raises:
        FileNotFoundError: If strategies_dir doesn't exist or is empty
        yaml.YAMLError: If any YAML file is invalid
        ValidationError: If any strategy config is invalid
    """
    if not strategies_dir.exists():
        raise FileNotFoundError(f"Strategy config directory not found: {strategies_dir}")

    strategies = {}
    yaml_files = list(strategies_dir.glob("*.yaml"))
    
    if not yaml_files:
        raise FileNotFoundError(f"No YAML configs found in {strategies_dir}")
        
    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            
        try:
            strategy = create_new_strategy(data, step_registry)
            strategies[strategy.name] = strategy
        except ValidationError as e:
            e.add_note(f"Invalid strategy config in {yaml_file}")
            raise
            
    return strategies
