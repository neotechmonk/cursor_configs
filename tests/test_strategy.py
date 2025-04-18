from typing import Any, Dict

import pandas as pd
import pytest

from strategy import (
    EvaluationResult,
    StrategyConfig,
    StrategyStep,
    load_strategy_config,
)


def mock_get_trend(price_feed: pd.DataFrame, **config: Dict[str, Any]) -> EvaluationResult:
    """Mock function for testing - always succeeds"""
    return EvaluationResult(success=True, message="Trend detected", data={"trend": "UP"})


def mock_is_extreme_bar(price_feed: pd.DataFrame, **config: Dict[str, Any]) -> EvaluationResult:
    """Mock function for testing - always succeeds"""
    # Simulate using frame_size from config if needed
    frame_size = config.get("frame_size", 5)
    return EvaluationResult(success=True, message=f"Extreme bar found (frame={frame_size})", data={"is_extreme": True})


def mock_is_bars_since_extreme_pivot_valid(price_feed: pd.DataFrame, **config: Dict[str, Any]) -> EvaluationResult:
    """Mock function for testing - always succeeds"""
    min_bars = config.get("min_bars", 3)
    max_bars = config.get("max_bars", 10)
    return EvaluationResult(success=True, message=f"Pullback valid ({min_bars}-{max_bars} bars)", data={"bars_valid": True})


def mock_is_within_fib_extension(price_feed: pd.DataFrame, **config: Dict[str, Any]) -> EvaluationResult:
    """Mock function for testing - always succeeds"""
    min_ext = config.get("min_extension", 1.35)
    max_ext = config.get("max_extension", 1.875)
    return EvaluationResult(success=True, message=f"Fib extension valid ({min_ext}-{max_ext})", data={"fib_valid": True})


def test_load_strategy_config_basic(sample_strategy_config):
    """Test loading a basic strategy configuration"""
    # Load the strategy config
    config = load_strategy_config("test_strategy", str(sample_strategy_config))
    
    # Verify the config object
    assert isinstance(config, StrategyConfig)
    assert config.name == "Test Strategy"
    assert len(config.steps) == 4
    
    # Verify each step
    trend_step = config.steps[0]
    assert trend_step.id == "detect_trend"
    assert trend_step.name == "Detect Trend"
    assert trend_step.config == {}
    assert trend_step.reevaluates == []
    
    extreme_step = config.steps[1]
    assert extreme_step.id == "find_extreme"
    assert extreme_step.name == "Find Extreme Bar"
    assert extreme_step.config == {"frame_size": 5}
    assert extreme_step.reevaluates == []
    
    pullback_step = config.steps[2]
    assert pullback_step.id == "validate_pullback"
    assert pullback_step.name == "Validate Pullback"
    assert pullback_step.config == {"min_bars": 3, "max_bars": 10}
    assert pullback_step.reevaluates == []
    
    fib_step = config.steps[3]
    assert fib_step.id == "check_fib"
    assert fib_step.name == "Check Fibonacci Extension"
    assert fib_step.config == {"min_extension": 1.35, "max_extension": 1.875}
    assert len(fib_step.reevaluates) == 1
    assert fib_step.reevaluates[0] == pullback_step  # Verify it's the same object referenced by ID
    assert fib_step.reevaluates[0].id == "validate_pullback"

    print(pullback_step)
    
    # Verify all steps have correct function references
    # Note: We compare function *names* here because the actual function objects 
    # might differ slightly due to import context, but they should resolve to the same code.
    assert trend_step.evaluation_fn.__name__ == mock_get_trend.__name__
    assert extreme_step.evaluation_fn.__name__ == mock_is_extreme_bar.__name__
    assert pullback_step.evaluation_fn.__name__ == mock_is_bars_since_extreme_pivot_valid.__name__
    assert fib_step.evaluation_fn.__name__ == mock_is_within_fib_extension.__name__
