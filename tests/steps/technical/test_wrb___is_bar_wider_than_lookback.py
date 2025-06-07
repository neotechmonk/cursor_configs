"""Tests for _is_bar_wider_than_lookback function in wrb.py"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.steps.technical.wrb import PriceLabel, _is_bar_wider_than_lookback


@pytest.fixture
def mock_data():
    """Create a minimal DataFrame with required structure.
    Note: 'open' column is not used in this function/test
    """
    # Day 1: range=10 (90-100)
    # Day 2: range=10 (100-110) 
    # Day 3: range=20 (115-135) : WRB  
    return pd.DataFrame({
        'high': [100, 110, 120],
        'low': [90, 90, 110],
        'close': [95, 115, 115]  
    }, index=pd.date_range('2024-01-01', periods=3))


@pytest.fixture
def mock_get_wide_range_bar():
    """Mock _get_wide_range_bar function."""
    with patch('src.steps.technical.wrb._get_wide_range_bar') as mock:
        yield mock


@pytest.fixture
def mock_get_high_low_range_abs():
    """Mock _get_high_low_range_abs function."""
    with patch('src.steps.technical.wrb._get_high_low_range_abs') as mock:
        yield mock


@pytest.fixture
def mock_calculate_lookup_reference_value():
    """Mock _calculate_lookup_reference_value function."""
    with patch('src.steps.technical.wrb._calculate_lookup_reference_value') as mock:
        yield mock


def test_no_wrb_detected(mock_data, mock_get_wide_range_bar):
    """Test when no wide range bar is detected.
    
    Steps in _is_bar_wider_than_lookback:
    1. Get WRB range and indices ❌ (returns nan, [])
    2. Check if min lookback bars are available ⏭️ (skipped due to step 1)
    3. Get lookback ranges ⏭️ (skipped due to step 1)
    4. Compare WRB range with lookback ranges ⏭️ (skipped due to step 1)
    """
    # Setup
    mock_get_wide_range_bar.return_value = (float('nan'), [])
    
    # Execute
    result = _is_bar_wider_than_lookback(
        data=mock_data,
        current_bar_index=mock_data.index[-1],
        lookback_bars=2,
        min_size_increase_pct=50.0
    )
    
    # Assert
    assert result is False
    mock_get_wide_range_bar.assert_called_once_with(
        price_data=mock_data,
        current_bar_index=mock_data.index[-1]
    )


def test_valid_wrb_max_comparison(mock_get_wide_range_bar, 
                                mock_calculate_lookup_reference_value):
    """Test valid wide range bar with max comparison method.
    
    This test focuses on the main functionality - verifying that a valid WRB is correctly identified.
    The internal calculations of reference values are tested separately in test_valid_wrb_verify_internal_calls.
    """
    # Setup mock data
    sample_data_single_bar_wrb = pd.DataFrame({
        PriceLabel.HIGH: [100, 110, 120],  # Last bar has higher high
        PriceLabel.LOW: [90, 90, 110],     # Last bar has higher low
        PriceLabel.CLOSE: [95, 115, 115]   # Last bar closes above previous high
    }, index=pd.date_range('2024-01-01', periods=3))
    
    current_idx = sample_data_single_bar_wrb.index[-1]
    
    # Mock WRB detection to return a valid range and indices
    mock_get_wide_range_bar.return_value = (20.0, [current_idx])
    
    # Mock reference value calculation - any value less than WRB range will work
    mock_calculate_lookup_reference_value.return_value = 10.0
    
    # Execute & assert
    assert _is_bar_wider_than_lookback(
        data=sample_data_single_bar_wrb,
        current_bar_index=current_idx,
        lookback_bars=2,
        min_size_increase_pct=1,  # 1% increase required
        comparison_method='max'
    )

def test_valid_wrb_avg_comparison(mock_get_wide_range_bar, 
                                mock_calculate_lookup_reference_value):
    """Test valid wide range bar with average comparison method.
    
    This test focuses on the main functionality - verifying that a valid WRB is correctly identified
    when using average comparison method. The internal calculations are tested separately.
    
    Test data setup:
    - Bar 1: range=8 (92-100)
    - Bar 2: range=12 (98-110)
    - Bar 3: range=20 (110-130) : WRB
    Average of lookback ranges = (8 + 12) / 2 = 10
    WRB range (20) > Average (10) * 1.01
    """
    # Setup mock data
    sample_data_single_bar_wrb = pd.DataFrame({
        PriceLabel.HIGH: [100, 110, 130],  # Last bar has higher high
        PriceLabel.LOW: [92, 98, 110],     # Last bar has higher low
        PriceLabel.CLOSE: [95, 115, 120]   # Last bar closes above previous high
    }, index=pd.date_range('2024-01-01', periods=3))
    
    current_idx = sample_data_single_bar_wrb.index[-1]
    
    # Mock WRB detection to return a valid range and indices
    mock_get_wide_range_bar.return_value = (20.0, [current_idx])
    
    # Mock reference value calculation
    # The function will receive [8.0, 12.0] as ranges and should return their average
    mock_calculate_lookup_reference_value.return_value = 10.0  # (8 + 12) / 2
    
    # Execute & assert
    result = _is_bar_wider_than_lookback(
        data=sample_data_single_bar_wrb,
        current_bar_index=current_idx,
        lookback_bars=2,
        min_size_increase_pct=1,  # 1% increase required
        comparison_method='avg'
    )
    
    # Verify the result and the mock call
    assert result is True
    mock_calculate_lookup_reference_value.assert_called_once_with([8.0, 12.0], 'avg')


def test_valid_wrb_verify_internal_calls(mock_data, mock_get_wide_range_bar, 
                                               mock_get_high_low_range_abs, 
                                               mock_calculate_lookup_reference_value):
    """Test internal function calls for valid wide range bar with max comparison.
    
    This test verifies that the internal functions are called correctly:
    1. _get_wide_range_bar is called with correct parameters
    2. _get_high_low_range_abs is called twice for lookback bars
    3. _calculate_lookup_reference_value is called with correct ranges and method
    """
    # Setup
    current_idx = mock_data.index[-1]
    
    # Mock WRB detection to return a valid range and indices
    mock_get_wide_range_bar.return_value = (20.0, [current_idx])
    
    # Mock lookback range calculations
    mock_get_high_low_range_abs.return_value = 10.0  # Lookback bars are 10.0 for the first two bars
    
    # Mock reference value calculation (max of lookback ranges)
    mock_calculate_lookup_reference_value.return_value = 10.0
    
    # Execute
    _is_bar_wider_than_lookback(
        data=mock_data,
        current_bar_index=current_idx,
        lookback_bars=2,
        min_size_increase_pct=1,
        comparison_method='max'
    )
    
    # Verify WRB detection was called correctly
    mock_get_wide_range_bar.assert_called_once_with(
        price_data=mock_data,
        current_bar_index=current_idx
    )
    
    # Verify lookback range calculations
    assert mock_get_high_low_range_abs.call_count == 2 # relates the first to bars
    
    # Verify reference value calculation
    mock_calculate_lookup_reference_value.assert_called_once_with([10.0, 10.0], 'max')




def test_zero_reference_value(mock_data, mock_get_wide_range_bar,
                            mock_get_high_low_range_abs,
                            mock_calculate_lookup_reference_value):
    """Test when reference value is zero."""
    # Setup
    wrb_range = 20.0
    current_idx = mock_data.index[-1]
    
    mock_get_wide_range_bar.return_value = (wrb_range, [current_idx])
    mock_get_high_low_range_abs.side_effect = [0.0, 0.0]  # Zero lookback ranges
    mock_calculate_lookup_reference_value.return_value = 0.0  # Zero reference
    
    # Execute & Assert
    with pytest.raises(ZeroDivisionError):
        _is_bar_wider_than_lookback(
            data=mock_data,
            current_bar_index=current_idx,
            lookback_bars=2,
            min_size_increase_pct=50.0
        )



def test_invalid_comparison_method(mock_get_wide_range_bar):
    """Test with invalid comparison method.
    
    This test verifies that the function raises a ValueError when an invalid
    comparison method is provided.
    """
    # Setup mock data with correct PriceLabel enum values
    sample_data = pd.DataFrame({
        PriceLabel.HIGH: [100, 110, 120],
        PriceLabel.LOW: [90, 100, 110],
        PriceLabel.CLOSE: [95, 105, 115]
    }, index=pd.date_range('2024-01-01', periods=3))
    
    current_idx = sample_data.index[-1]
    
    # Mock WRB detection to return a valid range and indices
    mock_get_wide_range_bar.return_value = (20.0, [current_idx])
    
    # Execute & Assert
    with pytest.raises(ValueError, match="Invalid comparison method"):
        _is_bar_wider_than_lookback(
            data=sample_data,
            current_bar_index=current_idx,
            lookback_bars=2,
            min_size_increase_pct=50.0,
            comparison_method='invalid'  # Invalid comparison method
        )



def test_invalid_index(mock_get_wide_range_bar):
    """Test with invalid index.
    
    This test verifies that the function raises an IndexError when an invalid
    index is provided that doesn't exist in the data.
    """
    # Setup mock data with correct PriceLabel enum values
    sample_data = pd.DataFrame({
        PriceLabel.HIGH: [100, 110, 120],
        PriceLabel.LOW: [90, 100, 110],
        PriceLabel.CLOSE: [95, 105, 115]
    }, index=pd.date_range('2024-01-01', periods=3))
    
    # Create an invalid index that doesn't exist in the data
    invalid_index = pd.Timestamp('2024-01-04')  # Not in sample_data
    
    # Mock WRB detection to raise IndexError for invalid index
    mock_get_wide_range_bar.side_effect = IndexError(f"Current bar index {invalid_index} not found in data")
    
    # Execute & Assert
    with pytest.raises(IndexError, match=f"Current bar index {invalid_index} not found in data"):
        _is_bar_wider_than_lookback(
            data=sample_data,
            current_bar_index=invalid_index,
            lookback_bars=2,
            min_size_increase_pct=50.0
        ) 