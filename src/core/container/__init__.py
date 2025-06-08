"""Container package for dependency injection.

This package provides containers for managing dependencies in the strategy system.
"""

from .step_registry import StepRegistryContainer
from .strategy import StrategyContainer

__all__ = ['StepRegistryContainer', 'StrategyContainer'] 
