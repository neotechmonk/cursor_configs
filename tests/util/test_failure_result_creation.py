"""Tests for failure result creation utility functions."""

import pandas as pd
import pytest

from src.models.strategy import StrategyStep
from src.utils import create_failure_result


@pytest.fixture
def sample_data():
    """Create sample price data for testing."""
    return pd.DataFrame({
        'open': [100, 101, 102],
        'high': [105, 106, 107],
        'low': [95, 96, 97],
        'close': [103, 104, 105]
    }, index=pd.date_range('2024-01-01', periods=3))


@pytest.fixture
def sample_step():
    """Create a sample strategy step for testing."""
    return StrategyStep(
        id="test_step_id",
        name="test_step",
        evaluation_fn=lambda x, y, z: None,
        description="Test step for unit testing",
        config={},
        reevaluates=[]
    )


def test_create_failure_result_with_error_msg(sample_data, sample_step):
    """Test creating a failure result with error message."""
    error_msg = "Test failure"
    step_output = {'error': 'details'}
    
    result = create_failure_result(sample_data, sample_step, error_msg=error_msg, step_output=step_output)
    
    assert result.is_success is False
    assert result.message == error_msg
    assert result.timestamp == sample_data.index[-1]
    assert result.step_output == step_output


def test_create_failure_result_with_exception(sample_data, sample_step):
    """Test creating a failure result with exception."""
    e = ValueError("Invalid input")
    
    result = create_failure_result(sample_data, sample_step, e=e)
    
    assert result.is_success is False
    assert result.message == f"Failed to complete {sample_step.name}: {str(e)}"
    assert result.timestamp == sample_data.index[-1]
    assert result.step_output == {}


def test_create_failure_result_with_both(sample_data, sample_step):
    """Test creating a failure result with both error message and exception."""
    error_msg = "Test failure"
    e = ValueError("Invalid input")
    
    result = create_failure_result(sample_data, sample_step, error_msg=error_msg, e=e)
    
    assert result.is_success is False
    assert result.message == f"{error_msg}: {str(e)}"
    assert result.timestamp == sample_data.index[-1]
    assert result.step_output == {}


def test_create_failure_result_defaults(sample_data, sample_step):
    """Test creating a failure result with no error message or exception."""
    result = create_failure_result(sample_data, sample_step)
    
    assert result.is_success is False
    assert result.message == f"Failed to complete {sample_step.name}"
    assert result.timestamp == sample_data.index[-1]
    assert result.step_output == {}


def test_empty_dataframe_failure(sample_step):
    """Test handling of empty DataFrame for failure result."""
    empty_data = pd.DataFrame()
    result = create_failure_result(empty_data, sample_step, error_msg="Error")
    assert result.timestamp is None 