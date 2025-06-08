"""
For a each new Bar
- keep track of steps
- need to know if a prior steps need to be revalidated
- transient info for future needs
"""

from enum import StrEnum
from importlib import import_module
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import yaml

from src.core.strategy_runner import _execute_strategy_step

# Import the moved models and types
from src.models import (
    StrategyConfig,
    StrategyExecutionContext,
    StrategyStep,
    StrategyStepEvaluationResult,
)


class StrategyStatus(StrEnum):
    """Possible states of a strategy execution.
    
    Attributes:
        NEW: Strategy has been created but not started
        SETUP_WIP: Strategy is in setup phase
        SETUP_CANCELLED: Setup phase was cancelled
        IN_TRADE: Strategy is in an active trade
        TRADE_WIP: Trade is being processed
        TRADE_CLOSED: Trade has been closed
    """
    NEW = "NEW"
    SETUP_WIP = "SETUP IN PROGRESS"
    SETUP_CANCELLED = "SETUP IN CANCELLED" 
    IN_TRADE = "IN TRADE"
    TRADE_WIP = "TRADE WIP"
    TRADE_CLOSED = "TRADE_CLOSED"


# class StrategyTracker(TypedDict):
#     Status : StrategyStatus
#     Steps: List[StrategyStep]


def load_strategy_config(strategy_name: str, config_dir: str = "configs/strategies") -> StrategyConfig:
    """Load strategy configuration from a YAML file.
    
    Args:
        strategy_name: Name of the strategy to load
        config_dir: Directory containing strategy configurations, relative to src/
        
    Returns:
        StrategyConfig object containing the strategy configuration
        
    Raises:
        FileNotFoundError: If the strategy configuration file doesn't exist
        ValueError: If the configuration file is invalid or contains errors:
            - Missing required fields (name, steps)
            - Missing step IDs
            - Duplicate step IDs
            - Invalid reevaluation references
            - Invalid YAML format
    """
    # Construct the full path to the config file
    config_path = Path(config_dir) / f"{strategy_name}.yaml"
    
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


def run_strategy(
    strategy: StrategyConfig, 
    price_feed: pd.DataFrame
) -> Tuple[StrategyExecutionContext, Dict[pd.Timestamp, Tuple[str, StrategyStepEvaluationResult]], List[Tuple[StrategyStep, StrategyStepEvaluationResult]]]:
    """Executes the strategy steps sequentially, managing execution context and history log.
    
    Args:
        strategy: The strategy configuration to execute
        price_feed: The price data to use for execution
        
    Returns:
        Tuple containing:
        - final execution context (latest results per step)
        - full history log (timestamp keyed)
        - list of executed steps in this run (step, result)
        
    Note:
        - Stops execution if a step fails or raises an error
        - Handles timestamp collisions in the history log
        - Validates step outputs before adding to context
    """
    executed_results_this_run: List[Tuple[StrategyStep, StrategyStepEvaluationResult]] = []
    current_context = StrategyExecutionContext() # Start with empty context (latest results)
    full_history_log: Dict[pd.Timestamp, Tuple[str, StrategyStepEvaluationResult]] = {} # Separate full log
    
    print(f"Running strategy: {strategy.name}")
    try:
        for i, step in enumerate(strategy.steps):
            print(f"  Executing step {i+1}: {step.name} (ID: {step.id})")
            
            # Execute step with the *current* context using imported function
            result = _execute_strategy_step(step, price_feed, current_context)
            executed_results_this_run.append((step, result))
            
            # Add result to the separate full history log using its timestamp
            # Handle potential timestamp collisions (unlikely but possible)
            timestamp_key = result.timestamp
            collision_counter = 0
            while timestamp_key in full_history_log:
                collision_counter += 1
                timestamp_key = result.timestamp + pd.Timedelta(nanoseconds=collision_counter)
                print(f"    Warning: Timestamp collision detected. Adjusting key for step {step.id} to {timestamp_key}")
            full_history_log[timestamp_key] = (step.id, result) 
            
            # Create the *next* context by adding the result immutably (with validation)
            # Pass the result's timestamp as the price_data_index
            next_context = current_context.add_result(result.timestamp, step, result) # Corrected call
            current_context = next_context # Move to the next state
            
            if result.is_success:
                print(f"    Success: {result.message or ''} {result.step_output or ''}")
            else:
                print(f"    Failed: {result.message or 'No message'}")
                print("  Strategy execution stopped due to step failure or error.")
                break # Stop on first failure
                
    except ValueError as ve: # Catch validation errors from add_result
        print(f"  Strategy execution stopped due to validation error: {ve}")
        # Potentially add a placeholder failure result for the step that triggered it?
        # For now, just stop and return what we have.
        pass
            
    print(f"Strategy execution finished: {strategy.name}")
    # Return the final context state, the full history log, and the list of results from this run
    return current_context, full_history_log, executed_results_this_run

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