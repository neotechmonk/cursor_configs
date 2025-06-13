"""Tests for StrategyExecutionContext class."""

import pandas as pd
import pytest

from src.models.strategy import (
    StrategyExecutionContext,
    StrategyStep,
    StrategyStepEvaluationResult,
)
from src.models.system import StrategyStepTemplate


@pytest.fixture
def step1():
    """Create a test step."""
    template = StrategyStepTemplate(
        system_step_id="step1",
        function="src.utils.get_trend",
        input_params_map={"price_data": "market.prices"},
        return_map={"trend": "_"}
    )
    return StrategyStep(
        system_step_id="step1",
        template=template,
        reevaluates=[]
    )


@pytest.fixture
def step2():
    """Create another test step."""
    template = StrategyStepTemplate(
        system_step_id="step2",
        function="src.utils.analyze_volume",
        input_params_map={"volume_data": "market.volumes"},
        return_map={"volume": "_"}
    )
    return StrategyStep(
        system_step_id="step2",
        template=template,
        reevaluates=[]
    )


@pytest.fixture
def ts1() -> pd.Timestamp:
    return pd.Timestamp("2023-01-01 10:00:00")


@pytest.fixture
def ts2() -> pd.Timestamp:
    return pd.Timestamp("2023-01-01 10:01:00")


@pytest.fixture
def context():
    """Create a test context."""
    return StrategyExecutionContext()

# @pytest.mark.skip()
def test_add_single_result(context, step1, ts1):
    """Test adding a single result to the context."""
    result = StrategyStepEvaluationResult(
        is_success=True,
        message="OK",
        step_output={"trend": "up"},
        timestamp=ts1
    )
    context.add_result(ts1, step1, result)
    assert context.get_latest_strategey_step_output_result("trend") == "up"


def test_add_multiple_unique_results(context, step1, step2, ts1, ts2):
    """Test adding multiple results from different steps."""
    result1 = StrategyStepEvaluationResult(
        is_success=True,
        message="OK",
        step_output={"trend": "up"},
        timestamp=ts1
    )
    result2 = StrategyStepEvaluationResult(
        is_success=True,
        message="OK",
        step_output={"volume": "high"},
        timestamp=ts2
    )
    
    context.add_result(ts1, step1, result1)
    context.add_result(ts2, step2, result2)
    
    assert context.get_latest_strategey_step_output_result("trend") == result1.step_output["trend"]
    assert context.get_latest_strategey_step_output_result("volume") == result2.step_output["volume"]


def test_add_overwriting_result_upon_success(context, step1, ts1, ts2):
    """Test that successful results overwrite previous results."""
    result1 = StrategyStepEvaluationResult(
        is_success=True,
        message="OK",
        step_output={"trend": "up"},
        timestamp=ts1
    )
    result2 = StrategyStepEvaluationResult(
        is_success=True,
        message="OK",
        step_output={"trend": "down"},
        timestamp=ts2
    )
    
    context.add_result(ts1, step1, result1)
    context.add_result(ts2, step1, result2)
    
    assert context.get_latest_strategey_step_output_result("trend") == result2.step_output["trend"]


def test_preserve_successful_result_upon_sebsequent_failure(context, step1, ts1, ts2):
    """Test that successful results are preserved upon subsequent failures."""
    result1 = StrategyStepEvaluationResult(
        is_success=True,
        message="OK",
        step_output={"trend": "up"},
        timestamp=ts1
    )
    result2 = StrategyStepEvaluationResult(
        is_success=False,
        message="Failed",
        step_output=None,
        timestamp=ts2
    )
    
    context.add_result(ts1, step1, result1)
    context.add_result(ts2, step1, result2)
    
    assert context.get_latest_strategey_step_output_result("trend") == result1.step_output["trend"]


def test_reject_duplicate_output_from_different_steps(context, ts1, ts2):
    """Test that duplicate output keys from different steps are rejected."""
    template1 = StrategyStepTemplate(
        system_step_id="step1",
        function="src.utils.get_trend",
        input_params_map={"price_data": "market.prices"},
        return_map={"trend": "_"}
    )
    template2 = StrategyStepTemplate(
        system_step_id="step2",
        function="src.utils.analyze_trend",
        input_params_map={"price_data": "market.prices"},
        return_map={"trend": "_"}
    )
    
    step1 = StrategyStep(
        system_step_id="step1",
        template=template1,
        reevaluates=[]
    )
    step2 = StrategyStep(
        system_step_id="step2",
        template=template2,
        reevaluates=[]
    )
    
    result1 = StrategyStepEvaluationResult(
        is_success=True,
        message="OK",
        step_output={"trend": "up"},
        timestamp=ts1
    )
    result2 = StrategyStepEvaluationResult(
        is_success=True,
        message="OK",
        step_output={"trend": "down"},
        timestamp=ts2
    )
    
    context.add_result(ts1, step1, result1)
    with pytest.raises(ValueError, match="produced identical output keys: \\['trend'\\]"):
        context.add_result(ts2, step2, result2) 