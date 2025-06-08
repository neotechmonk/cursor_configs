"""Main application entry point."""

import argparse
from pathlib import Path
from typing import Any, Dict

import yaml

from src.core.container import StepRegistryContainer, StrategyContainer
from src.core.strategy_runner import StrategyRunner


def load_price_data(file_path: str) -> Dict[str, Any]:
    """Load price data from file.
    
    Args:
        file_path: Path to price data file
        
    Returns:
        Price data dictionary
        
    Raises:
        FileNotFoundError: If file not found
        ValueError: If file format is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Price data file not found: {file_path}")
        
    with open(path) as f:
        data = yaml.safe_load(f)
        
    if not isinstance(data, dict):
        raise ValueError("Price data must be a dictionary")
        
    return data


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Trading Strategy System")
    parser.add_argument("--config", default="configs/config.yaml", help="Path to config file")
    parser.add_argument("--strategy", required=True, help="Strategy name to run")
    parser.add_argument("--data", required=True, help="Path to price data file")
    args = parser.parse_args()
    
    # Load config
    with open(args.config) as f:
        config = yaml.safe_load(f)
    
    # Initialize containers
    step_registry = StepRegistryContainer()
    step_registry.config.from_dict({
        "steps_dir": config["steps_dir"],
        "steps_config": config["steps_config"]
    })
    
    strategy_container = StrategyContainer()
    strategy_container.config.from_dict({
        "strategies_dir": config["strategies_dir"]
    })
    strategy_container.step_registry.override(step_registry.registry)
    
    # Load strategy
    strategy = strategy_container.strategy(args.strategy)
    
    # Load price data
    price_data = load_price_data(args.data)
    
    # Run strategy
    runner = StrategyRunner()
    results = runner.run_strategy(strategy, price_data)
    
    # Print results
    print(f"\nStrategy Results for {args.strategy}:")
    print("=" * 50)
    for step in strategy.steps:
        print(f"\nStep: {step.name}")
        print(f"Description: {step.description}")
        print(f"Result: {results[step.id]}")


if __name__ == "__main__":
    main() 