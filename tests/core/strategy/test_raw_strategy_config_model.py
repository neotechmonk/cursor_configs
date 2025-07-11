import pytest
from pydantic import ValidationError

from core.strategy.model import RawStrategyConfig, RawStrategyStepInstance


@pytest.fixture
def valid_strategy_dict():
    return {
        "name": "Trend Following Strategy",
        "steps": [
            {
                "id": "check_fib",
                "description": "Verify if price action meets Fibonacci extension criteria",
                "config_bindings": {},
                "runtime_bindings": {
                    "trend": "trend",
                    "ref_swing_start_idx": "bar_index_start",
                    "ref_swing_end_idx": "bar_index_end"
                },
                "reevaluates": ["validate_pullback"]
            }
        ]
    }


def test_raw_strategy_config_valid(valid_strategy_dict):
    """Test that a valid strategy dict creates a valid RawStrategyConfig."""
    config = RawStrategyConfig(**valid_strategy_dict)

    assert config.name == "Trend Following Strategy"
    assert len(config.steps) == 1
    step = config.steps[0]
    assert step.id == "check_fib"
    assert step.runtime_bindings["trend"] == "trend"


def test_missing_required_fields():
    """Test validation fails when required fields are missing."""
    invalid = {
        "steps": [
            {
                "description": "Missing ID and runtime_bindings",
                "config_bindings": {}
            }
        ]
    }
    with pytest.raises(ValidationError):
        RawStrategyConfig(**invalid)


def test_extra_fields_are_rejected(valid_strategy_dict):
    """Test that extra/unknown fields are rejected."""
    valid_strategy_dict["unknown"] = "surprise"
    with pytest.raises(ValidationError):
        RawStrategyConfig(**valid_strategy_dict)


def test_empty_reevaluates_defaults_to_list(valid_strategy_dict):
    """Test that reevaluates defaults to list when missing."""
    del valid_strategy_dict["steps"][0]["reevaluates"]
    config = RawStrategyConfig(**valid_strategy_dict)
    assert config.steps[0].reevaluates == []