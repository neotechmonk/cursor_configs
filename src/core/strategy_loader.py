"""Strategy loader module."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from src.models.strategy import StrategyConfig
from src.models.system import StrategyStepRegistry


class StrategyLoader:
    """Loads and validates strategy configurations."""
    
    def __init__(self, registry: StrategyStepRegistry):
        """Initialize strategy loader.
        
        Args:
            registry: Strategy step registry for validation
        """
        self.registry = registry
    
    def load_strategy(self, name: str, config_dir: str) -> StrategyConfig:
        """Load a strategy by name.
        
        Args:
            name: Strategy name (without .yaml extension)
            config_dir: Directory containing strategy configs
            
        Returns:
            Loaded and validated strategy config
            
        Raises:
            FileNotFoundError: If strategy config not found
            ValueError: If strategy config is invalid
        """
        config_path = Path(config_dir) / f"{name}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Strategy config not found: {config_path}")
            
        with open(config_path) as f:
            config = yaml.safe_load(f)
            
        return self._create_strategy_config(name, config)
    
    def _create_strategy_config(self, name: str, config: Dict[str, Any]) -> StrategyConfig:
        """Create a strategy config from config dict.
        
        Args:
            name: Strategy name
            config: Strategy configuration
            
        Returns:
            Created strategy config
            
        Raises:
            ValueError: If config is invalid
        """
        # Validate required fields
        required_fields = ["steps"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
                
        # Create strategy config
        steps = []
        for step_config in config["steps"]:
            step = self.registry.get_step(step_config)
            steps.append(step)
        
        return StrategyConfig(
            name=name,
            steps=steps
        ) 