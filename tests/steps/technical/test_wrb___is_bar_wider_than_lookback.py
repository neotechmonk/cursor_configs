"""Tests for _is_bar_wider_than_lookback function in wrb.py"""

from unittest.mock import patch

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


# ===== Basic WRB Detection Tests =====

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


# ===== Single Bar WRB Tests =====

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
    assert mock_get_high_low_range_abs.call_count == 2  # relates to the first two bars
    
    # Verify reference value calculation
    mock_calculate_lookup_reference_value.assert_called_once_with([10.0, 10.0], 'max')


# ===== Series WRB Tests =====

def test_valid_wrb_series_max_comparison(mock_get_wide_range_bar, 
                                       mock_calculate_lookup_reference_value,
                                       mock_get_high_low_range_abs):
    """Test valid wide range bar series with max comparison method.
    
    This test focuses on verifying that a valid WRB series is correctly identified.
    The series consists of 5 bars where the last 2 bars form a WRB series in an uptrend:
    
    Bar 1: range=10 (90-100) - normal bar
    Bar 2: range=10 (100-110) - normal bar
    Bar 3: range=10 (110-120) - normal bar
    Bar 4: range=15 (120-135) - WRB start: higher high, higher low, close above prev high
    Bar 5: range=20 (130-150) - WRB continuation: higher high, higher low, close above prev high
    
    The WRB series range is 30 (150-120) as it spans the last two bars.
    Lookback bars (2 and 3) have ranges of 10 each.
    """
    # Setup mock data for a series of WRBs
    sample_data_series_wrb = pd.DataFrame({
        PriceLabel.HIGH: [100, 110, 120, 135, 150],  # Last two bars have higher highs
        PriceLabel.LOW: [90, 100, 110, 120, 130],    # Last two bars have higher lows
        PriceLabel.CLOSE: [95, 105, 115, 140, 145]   # Last two bars close above previous highs
    }, index=pd.date_range('2024-01-01', periods=5))
    
    current_idx = sample_data_series_wrb.index[-1]
    fake_lookback_side_effect = [10.0, 10.0]
    
    # Mock WRB detection to return the series range and last two indices
    mock_get_wide_range_bar.return_value = (30.0, list(sample_data_series_wrb.index[-2:]))
    
    # Mock lookback range calculations to return 10.0 for both lookback bars
    mock_get_high_low_range_abs.side_effect = fake_lookback_side_effect
    
    # Mock reference value calculation - any value less than WRB range will work
    mock_calculate_lookup_reference_value.return_value = 10.0  # Max of lookback ranges (10, 10)
    
    # Execute & assert
    assert _is_bar_wider_than_lookback(
        data=sample_data_series_wrb,
        current_bar_index=current_idx,
        lookback_bars=2,
        min_size_increase_pct=1,  # 1% increase required
        comparison_method='max'
    )


def test_valid_wrb_series_avg_comparison(mock_get_wide_range_bar, 
                                       mock_calculate_lookup_reference_value,
                                       mock_get_high_low_range_abs):
    """Test valid wide range bar series with average comparison method.
    
    This test focuses on verifying that a valid WRB series is correctly identified
    when using average comparison method. The series consists of 5 bars where the
    last 2 bars form a WRB series in a downtrend:
    
    Bar 1: range=10 (100-90) - normal bar
    Bar 2: range=10 (90-80) - normal bar
    Bar 3: range=10 (80-70) - normal bar
    Bar 4: range=15 (75-60) - WRB start: lower high, lower low, close below prev low
    Bar 5: range=20 (60-40) - WRB continuation: lower high, lower low, close below prev low
    
    The WRB series range is 35 (75-40) as it spans the last two bars.
    Lookback bars (2 and 3) have ranges of 10 each.
    Average of lookback ranges = (10 + 10) / 2 = 10
    WRB range (35) > Average (10) * 1.01
    """
    # Setup mock data for a series of WRBs in downtrend
    sample_data_series_wrb = pd.DataFrame({
        PriceLabel.HIGH: [100, 90, 80, 75, 60],    # Last two bars have lower highs
        PriceLabel.LOW: [90, 80, 70, 60, 40],      # Last two bars have lower lows
        PriceLabel.CLOSE: [85, 75, 65, 55, 45]     # Last two bars close below previous lows
    }, index=pd.date_range('2024-01-01', periods=5))
    
    current_idx = sample_data_series_wrb.index[-1]
    fake_lookback_side_effect = [10.0, 10.0]
    
    # Mock WRB detection to return the series range and last two indices
    mock_get_wide_range_bar.return_value = (35.0, list(sample_data_series_wrb.index[-2:]))
    
    # Mock lookback range calculations to return 10.0 for both lookback bars
    mock_get_high_low_range_abs.side_effect = fake_lookback_side_effect
    
    # Mock reference value calculation
    # The function will receive [10.0, 10.0] as ranges and should return their average
    mock_calculate_lookup_reference_value.return_value = 10.0  # (10 + 10) / 2
    
    # Execute & assert
    result = _is_bar_wider_than_lookback(
        data=sample_data_series_wrb,
        current_bar_index=current_idx,
        lookback_bars=2,
        min_size_increase_pct=1,  # 1% increase required
        comparison_method='avg'
    )
    
    # Verify the result and the mock call
    assert result is True
    mock_calculate_lookup_reference_value.assert_called_once_with(fake_lookback_side_effect, 'avg')


# ===== Error Handling Tests =====

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