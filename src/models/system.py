"""Registry of available strategy step templates."""

import os
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Always resolve path relative to this file
DEFAULT_REGISTRY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "configs", "strategy_steps.yaml")


class StrategyStepTemplate(BaseModel):
    """A template for a single strategy step.
    
    Attributes:
        system_step_id: Unique identifier for the step in the system (e.g. "trend_following_detect_trend")
        function: The name of the function to execute
        input_params_map: Mapping of function parameter names to their source names
        return_map: Mapping of return value names (use "_" for direct value)
        config_mapping: Mapping of configuration parameter names to their source names
    """
    model_config = ConfigDict(frozen=True)
    
    system_step_id: str = Field(..., description="Unique identifier for the step in the system")
    function: str = Field(..., description="Name of the function to execute")
    input_params_map: Dict[str, str] = Field(default_factory=dict, description="Function parameter name to source name mapping")
    return_map: Dict[str, str] = Field(default_factory=dict, description="Return value name mapping (use '_' for direct value)")
    config_mapping: Dict[str, str] = Field(default_factory=dict, description="Configuration parameter name to source name mapping")

    @classmethod
    def _validate_not_empty(cls, v: str, field_name: str) -> str:
        if not v or not v.strip():
            raise ValueError(f"{field_name} cannot be empty")
        return v

    @field_validator('function')
    @classmethod
    def function_not_empty(cls, v):
        return cls._validate_not_empty(v, "Function name")
        
    @field_validator('system_step_id')
    @classmethod
    def system_step_id_not_empty(cls, v):
        return cls._validate_not_empty(v, "System step ID")


class StrategyStepRegistry(BaseModel):
    """Registry of all available strategy step templates.
    
    This class loads and validates strategy step templates from a YAML configuration file.
    The configuration should follow this structure:
    
    ```yaml
    steps:
      trend_following_detect_trend:
        function: "src.utils.get_trend"
        input_params_map:
          param1: source1
        return_map:
          result1: "_"  # Direct value
          result2: new_name  # Renamed value
        config_mapping:
          config1: source1
    ```
    """
    model_config = ConfigDict(frozen=True)
    
    steps: Dict[str, StrategyStepTemplate] = Field(
        default_factory=dict,
        description="Step names and mapping of parameters and result payload"
    )

    # @classmethod
    # def from_yaml(cls, yaml_file: str = DEFAULT_REGISTRY_FILE) -> 'StrategyStepRegistry':
    #     """Create a registry from a YAML file.
        
    #     Args:
    #         yaml_file: Path to the YAML file
            
    #     Returns:
    #         A new StrategyStepRegistry instance
            
    #     Raises:
    #         FileNotFoundError: If the YAML file doesn't exist
    #         yaml.YAMLError: If the YAML file is invalid
    #         ValueError: If the YAML content is invalid
    #     """
    #     if not os.path.exists(yaml_file):
    #         raise FileNotFoundError(f"YAML file not found: {yaml_file}")
            
    #     with open(yaml_file, 'r') as f:
    #         data = yaml.safe_load(f)
            
    #     if not isinstance(data, dict) or 'steps' not in data:
    #         raise ValueError("YAML must contain a 'steps' key with step definitions")
            
    #     steps = {}
    #     for system_step_id, step_data in data['steps'].items():
    #         steps[system_step_id] = StrategyStepTemplate(system_step_id=system_step_id, **step_data)
            
    #     return cls(steps=steps)

    def get_step_template(self, system_step_id: str) -> StrategyStepTemplate:
        """Get a step template by system step ID.
        
        Args:
            system_step_id: System ID of the step template to retrieve
            
        Returns:
            The requested step template
            
        Raises:
            KeyError: If the step template doesn't exist
        """
        if system_step_id not in self.steps:
            raise KeyError(f"Step '{system_step_id}' not found in registry")
        return self.steps[system_step_id]

    @property
    def step_template_names(self) -> List[str]:
        """Get a list of all system step IDs."""
        return list(self.steps.keys())

    @property
    def step_templates(self) -> List[StrategyStepTemplate]:
        """Get a list of all step templates."""
        return list(self.steps.values()) 