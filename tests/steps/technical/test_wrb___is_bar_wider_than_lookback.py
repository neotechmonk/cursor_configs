"""Tests for _is_bar_wider_than_lookback function in wrb.py

This module tests the comparison logic of _is_bar_wider_than_lookback function.
The function is responsible for comparing a WRB range against lookback ranges
and determining if the WRB is significantly wider.
"""

from unittest.mock import patch

import pytest

from src.steps.technical.wrb import _is_bar_wider_than_lookback


@pytest.fixture
def mock_calculate_lookup_reference_value():
    """Mock _calculate_lookup_reference_value function."""
    with patch('src.steps.technical.wrb._calculate_lookup_reference_value') as mock:
        yield mock


# ===== Basic Comparison Tests =====

def test_wider_than_lookback_max_comparison(mock_calculate_lookup_reference_value):
    """Test when WRB range is wider than lookback ranges using max comparison.
    
    Given:
    - WRB range: 20.0
    - Lookback ranges: [8.0, 10.0]
    - Min size increase: 50%
    - Comparison method: max
    
    When:
    - Max of lookback ranges is 10.0
    - Size increase is 100% (20.0/10.0 - 1)
    
    Then:
    - Should return True as 100% > 50%
    """
    # Setup
    mock_calculate_lookup_reference_value.return_value = 10.0
    
    # Execute
    result = _is_bar_wider_than_lookback(
        wrb_range=20.0,
        lookback_ranges=[8.0, 10.0],
        min_size_increase_pct=0.5,
        comparison_method='max'
    )
    
    # Assert
    assert result is True
    mock_calculate_lookup_reference_value.assert_called_once_with([8.0, 10.0], 'max')


def test_wider_than_lookback_avg_comparison(mock_calculate_lookup_reference_value):
    """Test when WRB range is wider than lookback ranges using avg comparison.
    
    Given:
    - WRB range: 20.0
    - Lookback ranges: [8.0, 10.0]
    - Min size increase: 50%
    - Comparison method: avg
    
    When:
    - Avg of lookback ranges is 9.0
    - Size increase is 122% (20.0/9.0 - 1)
    
    Then:
    - Should return True as 122% > 50%
    """
    # Setup
    mock_calculate_lookup_reference_value.return_value = 9.0
    
    # Execute
    result = _is_bar_wider_than_lookback(
        wrb_range=20.0,
        lookback_ranges=[8.0, 10.0],
        min_size_increase_pct=0.5,
        comparison_method='avg'
    )
    
    # Assert
    assert result is True
    mock_calculate_lookup_reference_value.assert_called_once_with([8.0, 10.0], 'avg')


def test_not_wider_than_lookback(mock_calculate_lookup_reference_value):
    """Test when WRB range is not wider than lookback ranges.
    
    Given:
    - WRB range: 15.0
    - Lookback ranges: [8.0, 10.0]
    - Min size increase: 50%
    - Comparison method: max
    
    When:
    - Max of lookback ranges is 10.0
    - Size increase is 50% (15.0/10.0 - 1)
    
    Then:
    - Should return True as 50% == 50% (not greater)
    """
    # Setup
    mock_calculate_lookup_reference_value.return_value = 10.0
    
    # Execute
    result = _is_bar_wider_than_lookback(
        wrb_range=15.0,
        lookback_ranges=[8.0, 10.0],
        min_size_increase_pct=0.5,
        comparison_method='max'
    )
    
    # Assert
    assert result is True
    mock_calculate_lookup_reference_value.assert_called_once_with([8.0, 10.0], 'max')


# ===== Error Cases =====

def test_zero_reference_value(mock_calculate_lookup_reference_value):
    """Test handling of zero reference value.
    
    Given:
    - WRB range: 20.0
    - Lookback ranges: [0.0, 0.0]
    - Min size increase: 50%
    
    When:
    - Reference value calculation raises ZeroDivisionError
    
    Then:
    - Should propagate the ZeroDivisionError
    """
    # Setup
    mock_calculate_lookup_reference_value.side_effect = ZeroDivisionError("Reference size is zero")
    
    # Execute & Assert
    with pytest.raises(ZeroDivisionError, match="Reference size is zero"):
        _is_bar_wider_than_lookback(
            wrb_range=20.0,
            lookback_ranges=[0.0, 0.0],
            min_size_increase_pct=0.5
        )


def test_invalid_comparison_method(mock_calculate_lookup_reference_value):
    """Test handling of invalid comparison method.
    
    Given:
    - WRB range: 20.0
    - Lookback ranges: [8.0, 10.0]
    - Min size increase: 50%
    - Invalid comparison method: 'invalid'
    
    When:
    - Reference value calculation raises ValueError
    
    Then:
    - Should propagate the ValueError
    """
    # Setup
    mock_calculate_lookup_reference_value.side_effect = ValueError("Invalid comparison method")
    
    # Execute & Assert
    with pytest.raises(ValueError, match="Invalid comparison method"):
        _is_bar_wider_than_lookback(
            wrb_range=20.0,
            lookback_ranges=[8.0, 10.0],
            min_size_increase_pct=0.5,
            comparison_method='invalid'
        ) 