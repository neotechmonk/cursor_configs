from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_REGISTRY_FILE = 'configs/strategies/strategy_steps.yaml'


class StrategyStepTemplate(BaseModel):
    """A template for a single strategy step.
    
    Attributes:
        pure_function: The name of the pure function to execute
        context_inputs: Mapping of input names to their types
        context_outputs: Mapping of output names to their types
        config_mapping: Mapping of configuration parameters
    """
    model_config = ConfigDict(frozen=True)
    
    pure_function: str = Field(..., description="Name of the pure function to execute")
    context_inputs: Dict[str, str] = Field(default_factory=dict, description="Input name to type mapping")
    context_outputs: Dict[str, str] = Field(default_factory=dict, description="Output name to type mapping")
    config_mapping: Dict[str, str] = Field(default_factory=dict, description="Configuration parameter mapping")

    @field_validator('pure_function')
    @classmethod
    def validate_pure_function(cls, v: str) -> str:
        """Validate that the pure function name is not empty."""
        if not v.strip():
            raise ValueError("Pure function name cannot be empty")
        return v.strip()


class StrategyStepRegistry(BaseSettings):
    """Registry of all available strategy step templates.
    
    This class loads and validates strategy step templates from a YAML configuration file.
    The configuration should follow this structure:
    
    ```yaml
    steps:
      step_name_1:
        pure_function: function_name
        context_inputs:
          input1: type1
        context_outputs:
          output1: type1
        config_mapping:
          param1: value1
    ```
    """
    model_config = SettingsConfigDict(
        frozen=True,
        extra='forbid',
        env_file_encoding='utf-8'
    )
    
    steps_data: Dict[str, StrategyStepTemplate] = Field(
        default_factory=dict,
        description="Step names and mapping of parameters and result payload",
        alias='steps'  # This maps the YAML 'steps' field to steps_data
    )

    def __init__(self, **kwargs):
        """Initialize the registry with YAML data."""
        if '_env_file' in kwargs:
            with open(kwargs['_env_file'], 'r', encoding='utf-8') as f:
                import yaml
                data = yaml.safe_load(f)
                kwargs['steps_data'] = data.get('steps', {})
        super().__init__(**kwargs)

    def get_step(self, step_name: str) -> StrategyStepTemplate:
        """Get a template by its name.
        
        Args:
            step_name: Name of the step template to retrieve
            
        Returns:
            The requested step template
            
        Raises:
            KeyError: If the step name doesn't exist in the registry
        """
        if step_name not in self.steps_data:
            raise KeyError(f"Step '{step_name}' not found in registry")
        return self.steps_data[step_name]

    @property
    def step_names(self) -> List[str]:
        """Get names of all steps in the registry.
        
        Returns:
            List of step names
        """
        return list(self.steps_data.keys())

    @property
    def step_objects(self) -> List[StrategyStepTemplate]:
        """Get all step template objects in the registry.
        
        Returns:
            List of StrategyStepTemplate objects
        """
        return list(self.steps_data.values())
