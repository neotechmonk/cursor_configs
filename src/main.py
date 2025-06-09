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
    
    strats = Provide[RootContainer.strategies.strategies]
):
    """
    Entry point for the application. Dependencies are injected.
    """
    print(strats.get("Trend Following Strategy"))


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get paths from environment variables
    project_root = Path(__file__).parent.parent
    strategies_dir = project_root / os.getenv("STRATEGIES_DIR", "configs/strategies")
    registry_file = project_root / os.getenv("STEP_REGISTRY_FILE", "configs/strategy_steps.yaml")
    
    # Initialize container with paths from environment
    container = RootContainer()
    container.config.strategies_dir.from_value(strategies_dir)
    container.config.step_registry.registry_file.from_value(registry_file)
    
    container.wire(modules=[__name__])
    
    # Run the application
    run_app()
