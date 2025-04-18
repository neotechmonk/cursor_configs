"""
For a each new Bar
- keep track of steps
- need to know if a prior steps need to be revalidated
- transient info for future needs
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pandas as pd  # Add pandas import
import yaml


class StrategyStatus (StrEnum):
    NEW = "NEW"
    SETUP_WIP = "SETUP IN PROGRESS"
    SETUP_CANCELLED = "SETUP IN CANCELLED" 
    IN_TRADE = "IN TRADE"
    TRADE_WIP = "TRADE WIP"
    TRADE_CLOSED = "TRADE_CLOSED"


@dataclass
class EvaluationResult:
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None # Optional data payload on success


@dataclass
class StrategyStepEvaluationResult:
    eval_time : datetime
    result : Optional[Any]


@dataclass
class StrategyStep:
    id: str  # Add unique identifier
    name: str
    description: str
    evaluation_fn: Callable
    config: Dict[str, Any]
    reevaluates: List['StrategyStep'] = field(default_factory=list)  # List of steps to reevaluate if this step fails


@dataclass
class StrategyConfig:
    name: str
    steps: List[StrategyStep]


# class StrategyTracker(TypedDict):
#     Status : StrategyStatus
#     Steps: List[StrategyStep]


def load_strategy_config(strategy_name: str, config_dir: str = "configs/strategies") -> StrategyConfig:
    """
    Load strategy configuration from a YAML file.
    
    Args:
        strategy_name: Name of the strategy to load
        config_dir: Directory containing strategy configurations, relative to src/
        
    Returns:
        StrategyConfig object containing the strategy configuration
        
    Raises:
        FileNotFoundError: If the strategy configuration file doesn't exist
        ValueError: If the configuration file is invalid or contains errors (missing IDs, duplicates, bad refs)
    """
    # Get the src directory path
    src_dir = Path(__file__).parent
    
    # Construct the full path to the config file
    config_path = src_dir / config_dir / f"{strategy_name}.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Strategy configuration file not found: {config_path}")
    
    try:
        config_data = yaml.safe_load(config_path.read_text())
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {str(e)}")
    
    if not isinstance(config_data, dict):
        raise ValueError("Configuration file must contain a dictionary")
    
    if "name" not in config_data:
        raise ValueError("Configuration must contain a 'name' field")
    
    if "steps" not in config_data:
        raise ValueError("Configuration must contain a 'steps' field")
    
    # First pass: Create all StrategyStep objects using IDs
    steps = []
    step_map = {}  # Map step IDs to StrategyStep objects
    for step_data in config_data["steps"]:
        if "id" not in step_data:
            raise ValueError(f"Configuration step missing 'id' field: {step_data.get('name', 'N/A')}")
        step_id = step_data["id"]
        if step_id in step_map:
            raise ValueError(f"Duplicate step ID found: {step_id}")
            
        # Import the evaluation function
        fn_path = step_data["evaluation_fn"]
        if "." in fn_path:
            # Import from module
            module_path, fn_name = fn_path.rsplit(".", 1)
            module = import_module(module_path)
            evaluation_fn = getattr(module, fn_name)
        else:
            # Import from current module
            evaluation_fn = globals()[fn_path]
        
        step = StrategyStep(
            id=step_id, # Use the ID from config
            name=step_data["name"],
            description=step_data["description"],
            evaluation_fn=evaluation_fn,
            config=step_data.get("config", {}),
            reevaluates=[]  # Initialize empty list, will be populated in second pass
        )
        steps.append(step)
        step_map[step.id] = step # Map using ID
    
    # Second pass: Set up reevaluation relationships using IDs
    for step_data, step in zip(config_data["steps"], steps):
        reevaluates_ids = step_data.get("reevaluates", {})
        for step_id_to_reevaluate, should_reevaluate in reevaluates_ids.items():
            if should_reevaluate:
                if step_id_to_reevaluate not in step_map:
                        raise ValueError(f"Step '{step.name}' (ID: {step.id}) references non-existent step ID for reevaluation: {step_id_to_reevaluate}")
                step.reevaluates.append(step_map[step_id_to_reevaluate]) # Use ID for lookup
    
    return StrategyConfig(
        name=config_data["name"],
        steps=steps
    )


# # FIX : refactor with App Runner
# def process_bar(price_feed : pd.DataFrame, tracker : StrategyTracker) :
#     new_bar = price_feed.iloc[-1]

#     match tracker.Status : 
#         case StrategyStatus.NEW:
#             pass
#         case StrategyStatus.SETUP_WIP:
#             pass
#         case StrategyStatus.SETUP_CANCELLED:
#             pass
#         case StrategyStatus.IN_TRADE:
#             pass