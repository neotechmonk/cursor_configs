"""Tests for time-related functionality."""

import pytest

from src.core.time import CustomTimeframe, TimeframeUnit


@pytest.mark.parametrize("value,unit,expected_str,expected_minutes,expected_pandas_offset", [
    (1, TimeframeUnit.MINUTE, "1m", 1, "1min"),
    (5, TimeframeUnit.MINUTE, "5m", 5, "5min"),
    (15, TimeframeUnit.MINUTE, "15m", 15, "15min"),
    (30, TimeframeUnit.MINUTE, "30m", 30, "30min"),
    (1, TimeframeUnit.HOUR, "1h", 60, "1H"),
    (4, TimeframeUnit.HOUR, "4h", 240, "4H"),
    (1, TimeframeUnit.DAY, "1d", 1440, "1D"),
    (1, TimeframeUnit.WEEK, "1w", 10080, "1W"),
    (1, TimeframeUnit.MONTH, "1M", 43200, "1M"),
    (1, TimeframeUnit.YEAR, "1y", 525600, "1Y"),
])
def test_custom_timeframe_creation(value, unit, expected_str, expected_minutes, expected_pandas_offset):
    """Test CustomTimeframe creation with various units."""
    timeframe = CustomTimeframe(value, unit)
    
    assert timeframe.value == value
    assert timeframe.unit == unit
    assert str(timeframe) == expected_str
    assert timeframe.minutes == expected_minutes
    assert timeframe.to_pandas_offset() == expected_pandas_offset


@pytest.mark.parametrize("timeframe_str,expected_value,expected_unit", [
    ("1m", 1, TimeframeUnit.MINUTE),
    ("5m", 5, TimeframeUnit.MINUTE),
    ("15m", 15, TimeframeUnit.MINUTE),
    ("30m", 30, TimeframeUnit.MINUTE),
    ("1h", 1, TimeframeUnit.HOUR),
    ("4h", 4, TimeframeUnit.HOUR),
    ("1d", 1, TimeframeUnit.DAY),
    ("1w", 1, TimeframeUnit.WEEK),
    ("1M", 1, TimeframeUnit.MONTH),
    ("1y", 1, TimeframeUnit.YEAR),
])
def test_custom_timeframe_from_string(timeframe_str, expected_value, expected_unit):
    """Test CustomTimeframe creation from string representation."""
    timeframe = CustomTimeframe(timeframe_str)
    
    assert timeframe.value == expected_value
    assert timeframe.unit == expected_unit
    assert str(timeframe) == timeframe_str


@pytest.mark.parametrize("invalid_string", [
    "",
    "invalid",
    "1",
    "m",
    "1x",
    "0m",
    "-1m",
])
def test_custom_timeframe_invalid_string(invalid_string):
    """Test CustomTimeframe creation with invalid strings."""
    with pytest.raises(ValueError):
        CustomTimeframe(invalid_string)


def test_timeframe_unit_properties():
    """Test TimeframeUnit properties."""
    # Test MINUTE
    assert TimeframeUnit.MINUTE.label == "minute"
    assert TimeframeUnit.MINUTE.short == "m"
    assert TimeframeUnit.MINUTE.pandas_offset == "min"
    assert TimeframeUnit.MINUTE.minutes == 1
    
    # Test HOUR
    assert TimeframeUnit.HOUR.label == "hour"
    assert TimeframeUnit.HOUR.short == "h"
    assert TimeframeUnit.HOUR.pandas_offset == "H"
    assert TimeframeUnit.HOUR.minutes == 60
    
    # Test DAY
    assert TimeframeUnit.DAY.label == "day"
    assert TimeframeUnit.DAY.short == "d"
    assert TimeframeUnit.DAY.pandas_offset == "D"
    assert TimeframeUnit.DAY.minutes == 1440


def test_timeframe_unit_from_short():
    """Test TimeframeUnit.from_short method."""
    assert TimeframeUnit.from_short("m") == TimeframeUnit.MINUTE
    assert TimeframeUnit.from_short("h") == TimeframeUnit.HOUR
    assert TimeframeUnit.from_short("d") == TimeframeUnit.DAY
    assert TimeframeUnit.from_short("w") == TimeframeUnit.WEEK
    assert TimeframeUnit.from_short("M") == TimeframeUnit.MONTH
    assert TimeframeUnit.from_short("y") == TimeframeUnit.YEAR
    
    with pytest.raises(ValueError, match="Unknown short code"):
        TimeframeUnit.from_short("x")


def test_custom_timeframe_equality():
    """Test CustomTimeframe equality and hashing."""
    tf1 = CustomTimeframe("5m")
    tf2 = CustomTimeframe("5m")
    tf3 = CustomTimeframe("10m")
    
    assert tf1 == tf2
    assert tf1 != tf3
    assert hash(tf1) == hash(tf2)
    
    # Test in sets
    timeframes = {tf1, tf2, tf3}
    assert len(timeframes) == 2  # tf1 and tf2 are equal, so only 2 unique items


def test_custom_timeframe_arithmetic():
    """Test CustomTimeframe arithmetic operations."""
    from datetime import datetime, timedelta
    
    tf = CustomTimeframe("1h")
    
    # Test __radd__ with datetime
    dt = datetime(2024, 1, 1, 12, 0)
    result = dt + tf
    assert result == datetime(2024, 1, 1, 13, 0)
    
    # Test __radd__ with timedelta
    td = timedelta(minutes=30)
    result = td + tf
    assert result == timedelta(hours=1, minutes=30)
    
    # Test __add__ with timedelta
    result = tf + timedelta(minutes=30)
    assert result == timedelta(hours=1, minutes=30) 