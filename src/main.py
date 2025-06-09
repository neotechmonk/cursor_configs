# app/main.py
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv

from core.container.root import RootContainer

# Load environment variables
load_dotenv()

# Initialize container with paths from environment
container = RootContainer()

# At module level
PROJECT_ROOT = Path(__file__).parent.parent
CONFIGS_DIR = PROJECT_ROOT / "configs"

# Then use these constants for configuration
container.config.strategies.dir.from_value(CONFIGS_DIR / "strategies")
container.config.step_registry.registry_file.from_value(CONFIGS_DIR / "strategy_steps.yaml")


@inject
def run_app(
    strategies = Provide[RootContainer.strategies.strategies]
):
    """
    Entry point for the application. Dependencies are injected.
    """
    strategy = strategies.get("Trend Following Strategy")
    print(strategy)


if __name__ == "__main__":
    container.wire(modules=[__name__])
    run_app()
