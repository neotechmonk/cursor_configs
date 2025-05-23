"""Strategy loader for creating strategy configurations from YAML files."""

from typing import Dict

import yaml

from src.core.registry_loader import RegistryLoader
from src.models import StrategyConfig, StrategyStep
from src.sandbox.evaluator import StepEvaluator


class StrategyLoader:
    def __init__(self, registry_loader: RegistryLoader):
        self.registry_loader = registry_loader
        
    def load_strategy(self, strategy_name: str, config_dir: str = "configs/strategies") -> StrategyConfig:
        """Load a specific strategy configuration."""
        config_path = f"{config_dir}/{strategy_name}.yaml"
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        if not isinstance(config_data, dict):
            raise ValueError("Strategy YAML must be a dictionary")
            
        steps = []
        step_map: Dict[str, StrategyStep] = {}
        
        # First pass: Create all steps
        for step_data in config_data["steps"]:
            step_id = step_data["id"]
            template = self.registry_loader.get_template(step_id)
            function = template.load_function()
            evaluator = StepEvaluator(template, function)
            
            step = StrategyStep(
                id=step_id,
                name=step_data["name"],
                evaluator=evaluator,
                description=step_data.get("description"),
                config=step_data.get("config", {}),
                reevaluates=[]  # Will be populated in second pass
            )
            steps.append(step)
            step_map[step_id] = step
            
        # Second pass: Set up reevaluation relationships
        for step_data, step in zip(config_data["steps"], steps):
            for reevaluate_id in step_data.get("reevaluates", []):
                if reevaluate_id not in step_map:
                    raise ValueError(f"Step '{step.name}' references non-existent step ID: {reevaluate_id}")
                step.reevaluates.append(step_map[reevaluate_id])
                
        return StrategyConfig(
            name=config_data["name"],
            steps=steps
        ) 