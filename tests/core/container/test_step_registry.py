"""Test script for StepRegistryContainer."""

from pathlib import Path

from models.system import StrategyStepRegistry
from src.core.container import StepRegistryContainer


def test_step_registry_loading():
    """Test loading of step registry container."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent.parent
        
    # # Initialize container
    container = StepRegistryContainer()
    
    # Configure container
    container.config.from_dict({
        "registry_file": str(project_root / "configs" / "strategy_steps.yaml")
    })
    
    # Get registry instance
    registry: StrategyStepRegistry = container.registry()
    
    # Print available steps
    print("\nAvailable Step Templates:")
    print("=" * 50)
    for step_name in registry.step_template_names:
        template = registry.get_step_template(step_name)
        print(f"\nStep: {step_name}")
        print(f"Function: {template.function}")
        print(f"Input Params: {template.input_params_map}")
        print(f"Return Map: {template.return_map}")
        print(f"Config Mapping: {template.config_mapping}")

