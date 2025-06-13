"""Core module for strategy execution."""

from src.loaders.strategy_config_loader import load_strategies
from src.loaders.step_registry_loader import load_step_registry

from .container import StepRegistryContainer, StrategiesContainer

__all__ = [
    'StepRegistryContainer',
    'StrategiesContainer',
    'load_strategies',
    'load_step_registry'
]
