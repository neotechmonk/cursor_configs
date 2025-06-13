"""Tests for the step registry container."""

from pathlib import Path

import pytest
import yaml

from src.core.container import StepRegistryContainer
from src.models.system import StrategyStepRegistry


@pytest.fixture
def mock_registry_file(tmp_path):
    """Create a mock registry file."""
    registry_file = tmp_path / "registry.yaml"
    registry = {
        "steps": {
            "mock_step": {
                "function": "mock.func",
                "input_params_map": {},
                "return_map": {},
                "config_mapping": {}
            }
        }
    }
    with open(registry_file, "w") as f:
        yaml.safe_dump(registry, f)
    return registry_file


def test_step_registry_container_creation(mock_registry_file):
    """Test creating a step registry container."""
    # Create container with required dependencies
    container = StepRegistryContainer()
    container.registry_file.override(mock_registry_file)
    
    # Wire container
    container.wire()
    
    # Verify registry is created
    assert container.registry() is not None
    assert isinstance(container.registry(), StrategyStepRegistry)


def test_step_registry_loading():
    """Test loading of step registry container."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent.parent
        
    # Initialize container
    container = StepRegistryContainer(
        registry_file=project_root / "configs" / "strategy_steps.yaml"
    )
    
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

