"""Tests for the detect_wide_range_bar function.

This module tests the main public interface for wide range bar detection.
The internal logic is tested in separate modules:
- test_wrb__get_wide_range_bar.py: Tests WRB pattern detection
- test_wrb___is_bar_wider_than_lookback.py: Tests range comparison logic
- test_wrb__calculate_lookup_reference_value.py: Tests reference value calculation
- test_wrb__validate_lookup_bars.py: Tests lookback validation
"""

from unittest.mock import Mock, patch

import pytest

from src.models.strategy import StrategyExecutionContext, StrategyStep
from src.steps.technical.wrb import detect_wide_range_bar


@pytest.fixture
def sample_data():
    """Create minimal sample price data for testing."""
    return Mock()  # Mock data since we'll mock all data operations


@pytest.fixture
def sample_context():
    """Create minimal strategy execution context for testing."""
    return StrategyExecutionContext(
        current_step=StrategyStep(
            name="test_step",
            description="Test step",
            config={}
        )
    )


@pytest.mark.skip(reason="Debugging one test at a time")
@patch('src.steps.technical.wrb.validate_lookback_period')
@patch('src.steps.technical.wrb.identify_wide_range_bar')
@patch('src.steps.technical.wrb.compare_bar_width')
def test_detect_wide_range_bar_success(
    mock_compare_width,
    mock_identify_wrb,
    mock_validate,
    sample_data,
    sample_context
):
    """Test successful detection of a wide range bar.
    
    This test verifies that the main function correctly:
    1. Validates input data
    2. Detects WRB pattern
    3. Compares with lookback bars
    4. Returns success result with correct output
    """
    # Setup mocks
    mock_validate.return_value = True
    mock_identify_wrb.return_value = (100.0, ['2024-01-01', '2024-01-02'])
    mock_compare_width.return_value = True
    
    config = {
        'lookback_bars': 2,
        'min_size_increase_pct': 50.0
    }
    
    result = detect_wide_range_bar(sample_data, sample_context, config)
    
    # Verify mock calls
    mock_validate.assert_called_once_with(sample_data, 2)
    mock_identify_wrb.assert_called_once()
    mock_compare_width.assert_called_once()
    
    # Verify result
    assert result.is_success
    assert result.step_output['is_wide_range'] is True
    assert result.step_output['lookback_bars'] == 2
    assert result.step_output['min_size_increase_pct'] == 50.0


@pytest.mark.skip(reason="Debugging one test at a time")
@patch('src.steps.technical.wrb.validate_lookback_period')
@patch('src.steps.technical.wrb.identify_wide_range_bar')
def test_detect_wide_range_bar_no_wrb(
    mock_identify_wrb,
    mock_validate,
    sample_data,
    sample_context
):
    """Test when no wide range bar is detected.
    
    This test verifies that the main function correctly:
    1. Returns success result even when no WRB is detected
    2. Includes correct configuration in output
    3. Sets is_wide_range to False
    """
    # Setup mocks
    mock_validate.return_value = True
    mock_identify_wrb.return_value = (float('nan'), [])  # No WRB detected
    
    config = {
        'lookback_bars': 2,
        'min_size_increase_pct': 200.0
    }
    
    result = detect_wide_range_bar(sample_data, sample_context, config)
    
    # Verify mock calls
    mock_validate.assert_called_once_with(sample_data, 2)
    mock_identify_wrb.assert_called_once()
    
    # Verify result
    assert result.is_success
    assert result.step_output['is_wide_range'] is False
    assert result.step_output['lookback_bars'] == 2
    assert result.step_output['min_size_increase_pct'] == 200.0


@pytest.mark.skip(reason="Debugging one test at a time")
@patch('src.steps.technical.wrb.validate_lookback_period')
def test_detect_wide_range_bar_insufficient_bars(
    mock_validate,
    sample_data,
    sample_context
):
    """Test with insufficient bars for lookback period.
    
    This test verifies that the main function correctly:
    1. Validates lookback period requirements
    2. Returns failure result with appropriate error message
    """
    # Setup mock
    mock_validate.return_value = False
    
    config = {
        'lookback_bars': 10,
        'min_size_increase_pct': 50.0
    }
    
    result = detect_wide_range_bar(sample_data, sample_context, config)
    
    # Verify mock call
    mock_validate.assert_called_once_with(sample_data, 10)
    
    # Verify result
    assert not result.is_success
    assert "Not enough bars for the lookback period" in result.error_msg


@pytest.mark.skip(reason="Debugging one test at a time")
@patch('src.steps.technical.wrb.validate_lookback_period')
def test_detect_wide_range_bar_validation_error(
    mock_validate,
    sample_data,
    sample_context
):
    """Test when validation raises an error.
    
    This test verifies that the main function correctly:
    1. Handles validation errors
    2. Returns failure result with appropriate error message
    """
    # Setup mock to raise error
    mock_validate.side_effect = ValueError("Invalid data")
    
    config = {
        'lookback_bars': 2,
        'min_size_increase_pct': 50.0
    }
    
    result = detect_wide_range_bar(sample_data, sample_context, config)
    
    # Verify mock call
    mock_validate.assert_called_once_with(sample_data, 2)
    
    # Verify result
    assert not result.is_success
    assert "Invalid price data format" in result.error_msg


@pytest.mark.skip(reason="Debugging one test at a time")
@patch('src.steps.technical.wrb.validate_lookback_period')
@patch('src.steps.technical.wrb.identify_wide_range_bar')
@patch('src.steps.technical.wrb.compare_bar_width')
def test_detect_wide_range_bar_zero_reference(
    mock_compare_width,
    mock_identify_wrb,
    mock_validate,
    sample_data,
    sample_context
):
    """Test when reference value calculation results in zero.
    
    This test verifies that the main function correctly:
    1. Handles zero reference value errors
    2. Returns failure result with appropriate error message
    """
    # Setup mocks
    mock_validate.return_value = True
    mock_identify_wrb.return_value = (100.0, ['2024-01-01', '2024-01-02'])
    mock_compare_width.side_effect = ZeroDivisionError("Reference size is zero")
    
    config = {
        'lookback_bars': 2,
        'min_size_increase_pct': 50.0
    }
    
    result = detect_wide_range_bar(sample_data, sample_context, config)
    
    # Verify mock calls
    mock_validate.assert_called_once_with(sample_data, 2)
    mock_identify_wrb.assert_called_once()
    mock_compare_width.assert_called_once()
    
    # Verify result
    assert not result.is_success
    assert "Cannot calculate size increase: average bar size is zero" in result.error_msg


@pytest.mark.skip(reason="Debugging one test at a time")
@patch('src.steps.technical.wrb.validate_lookback_period')
@patch('src.steps.technical.wrb.identify_wide_range_bar')
@patch('src.steps.technical.wrb.compare_bar_width')
def test_detect_wide_range_bar_default_config(
    mock_compare_width,
    mock_identify_wrb,
    mock_validate,
    sample_data,
    sample_context
):
    """Test with default configuration values.
    
    This test verifies that the main function correctly:
    1. Uses default values when config is empty
    2. Returns success result with default values in output
    """
    # Setup mocks
    mock_validate.return_value = True
    mock_identify_wrb.return_value = (100.0, ['2024-01-01', '2024-01-02'])
    mock_compare_width.return_value = True
    
    # Empty config should use defaults
    config = {}
    
    result = detect_wide_range_bar(sample_data, sample_context, config)
    
    # Verify mock calls with default values
    mock_validate.assert_called_once_with(sample_data, 20)  # Default lookback_bars
    mock_identify_wrb.assert_called_once()
    mock_compare_width.assert_called_once()
    
    # Verify result
    assert result.is_success
    assert result.step_output['lookback_bars'] == 20  # Default value
    assert result.step_output['min_size_increase_pct'] == 50.0  # Default value 