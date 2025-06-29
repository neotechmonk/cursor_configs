"""Loader for step registry configurations."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from models.system import StrategyStepRegistry, StrategyStepTemplate


def create_step_template(template_data: dict) -> StrategyStepTemplate:
    """Create a step template from template data.
    
    Args:
        template_data: Dictionary containing template configuration
        
    Returns:
        StrategyStepTemplate object
        
    Raises:
        ValidationError: If template data is invalid
    """
    return StrategyStepTemplate(**template_data)


def load_step_registry(
    registry_file: Path = Path("configs/strategy_steps.yaml"),
) -> StrategyStepRegistry:
    """Load step registry configuration from YAML file.
    
    Args:
        registry_file: Path to the registry YAML file
        
    Returns:
        StrategyStepRegistry object
        
    Raises:
        FileNotFoundError: If registry file doesn't exist
        yaml.YAMLError: If YAML file is invalid
        ValidationError: If registry data is invalid
    """
    if not registry_file.exists():
        raise FileNotFoundError(f"Registry file not found: {registry_file}")
        
    with open(registry_file, 'r') as f:
        data = yaml.safe_load(f)
        
    if not isinstance(data, dict) or 'steps' not in data:
        raise ValueError("YAML must contain a 'steps' key with step definitions")
        
    # Create templates with system_step_id from the step key
    steps = {}
    for system_step_id, step_data in data['steps'].items():
        # Add system_step_id to the template data
        template_data = {**step_data, 'system_step_id': system_step_id}
        steps[system_step_id] = create_step_template(template_data)
        
    try:
        return StrategyStepRegistry(steps=steps)
    except ValidationError as e:
        e.add_note(f"Invalid registry config in {registry_file}")
        raise 