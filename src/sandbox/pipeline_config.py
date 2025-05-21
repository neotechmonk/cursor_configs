"""Pipeline configuration loader for strategy steps."""

import os
from typing import Any, Dict

import yaml


class PipelineConfig:
    """Loads and manages pipeline configuration for strategy steps."""
    
    def __init__(self, config_path: str):
        """Initialize with path to config file.
        
        Args:
            config_path: Path to YAML configuration file
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate the configuration structure."""
        if 'steps' not in self.config:
            raise ValueError("Configuration must contain 'steps' section")
            
        for step_name, step_config in self.config['steps'].items():
            required_keys = ['pure_function', 'context_inputs', 'context_outputs', 'config_mapping']
            missing_keys = [key for key in required_keys if key not in step_config]
            if missing_keys:
                raise ValueError(f"Step '{step_name}' missing required keys: {missing_keys}")
    
    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        """Get configuration for a specific step.
        
        Args:
            step_name: Name of the step to get configuration for
            
        Returns:
            Dictionary containing step configuration
            
        Raises:
            KeyError: If step_name is not found in configuration
        """
        if step_name not in self.config['steps']:
            raise KeyError(f"Step '{step_name}' not found in configuration")
        return self.config['steps'][step_name]
    
    def get_all_step_names(self) -> list[str]:
        """Get list of all step names in configuration.
        
        Returns:
            List of step names
        """
        return list(self.config['steps'].keys())
    
    def _get_value_from_path(self, obj: Dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation path.
        
        Args:
            obj: Dictionary to get value from
            path: Dot notation path (e.g. "config.trend.min_bars")
            
        Returns:
            Value at path
            
        Raises:
            KeyError: If path is invalid
        """
        current = obj
        for key in path.split('.'):
            if key not in current:
                raise KeyError(f"Path '{path}' not found in object")
            current = current[key]
        return current 