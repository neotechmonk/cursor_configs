"""Loader for strategy configurations."""

from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import ValidationError

from src.models.strategy import StrategyConfig, StrategyStep
from src.models.system import StrategyStepRegistry, StrategyStepTemplate


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
    if not config_dir.exists():
        raise FileNotFoundError(f"Strategy config directory not found: {config_dir}")
        
    strategies = {}
    for yaml_file in config_dir.glob("*.yaml"):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            
        # Convert steps to StrategyStep objects
        steps = []
        for step_data in data['steps']:
            # Get template if registry is provided
            template = step_registry.get_step_template(step_data['system_step_id'])

            # Create step with template
            step = StrategyStep(template=template, **step_data)
            steps.append(step)
            
        # Create strategy config - Pydantic will validate required fields
        try:
            strategy = StrategyConfig(name=data['name'], steps=steps)
            strategies[strategy.name] = strategy
        except ValidationError as e:
            raise ValidationError(
                f"Invalid strategy config in {yaml_file}: {str(e)}",
                StrategyConfig
            )
            
    return strategies 