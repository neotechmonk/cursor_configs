"""Generic YAML configuration loader.

This module provides a universal YAML configuration loader that can:
- Load raw YAML data as dictionaries
- Validate and instantiate Pydantic models from YAML
- Handle validation errors with helpful error messages
"""

from pathlib import Path
from typing import Optional, Type, TypeVar, Union

import yaml
from pydantic import BaseModel, ValidationError

# Type variable for config classes (must be BaseModel or similar)
CONFIG_CLASS = TypeVar('CONFIG_CLASS', bound=BaseModel)


def load_yaml_config(
    config_path: Path,
    config_class: Optional[Type[CONFIG_CLASS]] = None,
) -> Union[CONFIG_CLASS, list[CONFIG_CLASS], dict, list]:
    """Load and optionally validate configuration from a YAML file.

    Load and optionally validate YAML configuration as a BaseModel or list of BaseModel.

    Automatically detects whether the YAML is a dict or list and applies validation accordingly.
    
    This function can load YAML files in two modes:
    1. Raw mode: Returns the YAML data as a dictionary or list
    2. Validated mode: Validates the data against a Pydantic model and returns an instance or list of instances
    
    Args:
        config_path: Path to the YAML configuration file
        config_class: Optional Pydantic model class for validation and instantiation.
                    If provided, the YAML data will be validated against this model.
                    If None, returns raw dictionary or list data.
        
    Returns:
        If config_class is provided: Validated config_class instance or list of instances
        If config_class is None: Raw dictionary or list from YAML
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        ValueError: If the YAML file is malformed or invalid
        ValidationError: If config_class is provided and validation fails
        
    Example:
        # Load raw YAML data
        raw_config = load_yaml_config(Path("config.yaml"))
        
        # Load and validate with Pydantic model
        config = load_yaml_config(Path("config.yaml"), MyConfigModel)
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with config_path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if config_class is None:
            return data

        if isinstance(data, list):
            return [config_class(**item) for item in data]
        elif isinstance(data, dict):
            return config_class(**data)
        else:
            raise ValueError(f"Unsupported YAML structure: {type(data)}")

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {config_path}: {e}")
    except ValidationError as e:
        e.add_note(f"Validation failed for config file: {config_path}")
        raise
