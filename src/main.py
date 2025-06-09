# app/main.py
import os
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv

from core.container.root import RootContainer
from loaders.strategy_config_loader import StrategyConfigLoader
from models.strategy import StrategyExecutionContext
from models.system import StrategyStepRegistry


@inject
def run_app(
    strategies_dir: str = Provide[RootContainer.config.strategies.strategies_dir],
    registry: StrategyStepRegistry = Provide[RootContainer.steps.registry]
):
    """
    Entry point for the application. Dependencies are injected.
    """
    print(f"Using strategies directory: {strategies_dir}")
    loader = StrategyConfigLoader(
        config_dir=Path(strategies_dir),
        step_registry=registry
    )
    strategy = loader.load_strategy("sample_strategy")
    context = StrategyExecutionContext()

    for step in strategy.steps:
        template = registry.get_step_template(step.system_step_id)
        print(f"Executing step: {step.system_step_id}")
        print(f"  Description: {step.description}")
        print(f"  Template: {template.function}")


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get paths from environment variables
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    strategies_dir = os.path.join(project_root, os.getenv("STRATEGIES_DIR", "configs/strategies"))
    registry_file = os.path.join(project_root, os.getenv("STEP_REGISTRY_FILE", "configs/strategy_steps.yaml"))
    
    # Initialize container with paths from environment
    container = RootContainer()
    container.config.strategies.strategies_dir.from_value(strategies_dir)
    container.config.step_registry.registry_file.from_value(registry_file)
    
    # Wire the container to this module
    container.wire(modules=[__name__])
    
    # Run the application
    run_app()
