import os
from typing import Dict, List

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Always resolve path relative to this file
DEFAULT_REGISTRY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "configs", "strategy_steps.yaml")


class StrategyStepTemplate(BaseModel):
    """A template for a single strategy step.
    
    Attributes:
        function: The name of the function to execute
        input_params_map: Mapping of function parameter names to their source names
        return_map: Mapping of return value names (use "_" for direct value)
        config_mapping: Mapping of configuration parameter names to their source names
    """
    model_config = ConfigDict(frozen=True)
    
    function: str = Field(..., description="Name of the function to execute")
    input_params_map: Dict[str, str] = Field(default_factory=dict, description="Function parameter name to source name mapping")
    return_map: Dict[str, str] = Field(default_factory=dict, description="Return value name mapping (use '_' for direct value)")
    config_mapping: Dict[str, str] = Field(default_factory=dict, description="Configuration parameter name to source name mapping")

    @field_validator('function')
    @classmethod
    def function_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Function name cannot be empty")
        return v


class StrategyStepRegistry(BaseModel):
    """Registry of all available strategy step templates.
    
    This class loads and validates strategy step templates from a YAML configuration file.
    The configuration should follow this structure:
    
    ```yaml
    steps:
      step_name_1:
        function: function_name
        input_params_map:
          param1: source1
        return_map:
          result1: "_"  # Direct value
          result2: new_name  # Renamed value
        config_mapping:
          config1: source1
    config_mapping:
      global_config1: source1
    ```
    """
    model_config = ConfigDict(frozen=True)
    
    steps: Dict[str, StrategyStepTemplate] = Field(
        default_factory=dict,
        description="Step names and mapping of parameters and result payload"
    )
    config_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Global configuration parameter name to source name mapping"
    )

    @classmethod
    def from_yaml(cls, yaml_file: str = DEFAULT_REGISTRY_FILE) -> 'StrategyStepRegistry':
        """Create a registry from a YAML file.
        
        Args:
            yaml_file: Path to the YAML file
            
        Returns:
            A new StrategyStepRegistry instance
            
        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            yaml.YAMLError: If the YAML file is invalid
            ValueError: If the YAML content is invalid
        """
        print(f"\nLoading YAML from: {yaml_file}")
        if not os.path.exists(yaml_file):
            raise FileNotFoundError(f"YAML file not found: {yaml_file}")
            
        with open(yaml_file, 'r') as f:
            content = f.read()
            print("YAML contents:")
            print(content)
            data = yaml.safe_load(content)
            
        if not isinstance(data, dict) or 'steps' not in data:
            raise ValueError("YAML must contain a 'steps' key with step definitions")
            
        steps = {}
        for step_name, step_data in data['steps'].items():
            steps[step_name] = StrategyStepTemplate(**step_data)
            
        config_mapping = data.get('config_mapping', {})
        return cls(steps=steps, config_mapping=config_mapping)

    def get_step_template(self, step_name: str) -> StrategyStepTemplate:
        if step_name not in self.steps:
            raise KeyError(f"Step '{step_name}' not found in registry")
        return self.steps[step_name]

    @property
    def step_template_names(self) -> List[str]:
        return list(self.steps.keys())

    @property
    def step_templates(self) -> List[StrategyStepTemplate]:
        return list(self.steps.values()) 