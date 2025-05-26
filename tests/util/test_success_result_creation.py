"""Tests for success result creation utility functions."""

import pandas as pd
import pytest

from src.models.strategy import StrategyStep
from src.utils import create_success_result


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


def test_create_success_result(sample_data, sample_step):
    """Test creating a successful result with custom message."""
    message = "Test success"
    step_output = {'key': 'value'}
    
    result = create_success_result(sample_data, sample_step, message, step_output)
    
    assert result.is_success is True
    assert result.message == message
    assert result.timestamp == sample_data.index[-1]
    assert result.step_output == step_output


def test_create_success_result_defaults(sample_data, sample_step):
    """Test creating a successful result with default values."""
    result = create_success_result(sample_data, sample_step)
    
    assert result.is_success is True
    assert result.message == f"Successfully completed {sample_step.name}"
    assert result.timestamp == sample_data.index[-1]
    assert result.step_output == {}


def test_empty_dataframe_success(sample_step):
    """Test handling of empty DataFrame for success result."""
    empty_data = pd.DataFrame()
    result = create_success_result(empty_data, sample_step)
    assert result.timestamp is None 