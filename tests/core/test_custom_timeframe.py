"""Tests for the new CustomTimeframe Pydantic model."""

import pytest

from src.core.time import CustomTimeframe, TimeframeUnit


class TestCustomTimeframeCreation:
    """Test CustomTimeframe creation with different constructors."""
    
    def test_create_from_string_minutes(self):
        """Test creating from string with minutes."""
        tf = CustomTimeframe("5m")
        assert tf.value == 5
        assert tf.unit == TimeframeUnit.MINUTE
        assert str(tf) == "5m"
    
    def test_create_from_string_hours(self):
        """Test creating from string with hours."""
        tf = CustomTimeframe("2h")
        assert tf.value == 2
        assert tf.unit == TimeframeUnit.HOUR
        assert str(tf) == "2h"
    
    def test_create_from_string_days(self):
        """Test creating from string with days."""
        tf = CustomTimeframe("1d")
        assert tf.value == 1
        assert tf.unit == TimeframeUnit.DAY
        assert str(tf) == "1d"
    
    def test_create_from_string_weeks(self):
        """Test creating from string with weeks."""
        tf = CustomTimeframe("1w")
        assert tf.value == 1
        assert tf.unit == TimeframeUnit.WEEK
        assert str(tf) == "1w"
    
    def test_create_from_string_months(self):
        """Test creating from string with months."""
        tf = CustomTimeframe("3M")
        assert tf.value == 3
        assert tf.unit == TimeframeUnit.MONTH
        assert str(tf) == "3M"
    
    def test_create_from_string_years(self):
        """Test creating from string with years."""
        tf = CustomTimeframe("1y")
        assert tf.value == 1
        assert tf.unit == TimeframeUnit.YEAR
        assert str(tf) == "1y"
    
    def test_create_from_value_and_unit(self):
        """Test creating from value and unit."""
        tf = CustomTimeframe(15, TimeframeUnit.MINUTE)
        assert tf.value == 15
        assert tf.unit == TimeframeUnit.MINUTE
        assert str(tf) == "15m"
    
    def test_create_from_value_and_unit_hours(self):
        """Test creating from value and unit with hours."""
        tf = CustomTimeframe(4, TimeframeUnit.HOUR)
        assert tf.value == 4
        assert tf.unit == TimeframeUnit.HOUR
        assert str(tf) == "4h"


class TestCustomTimeframeValidation:
    """Test validation of CustomTimeframe."""
    
    def test_invalid_empty_string(self):
        """Test that empty string raises error."""
        with pytest.raises(ValueError, match="Empty timeframe string"):
            CustomTimeframe("")
    
    def test_invalid_string_format(self):
        """Test that invalid string format raises error."""
        with pytest.raises(ValueError, match="Invalid timeframe string format"):
            CustomTimeframe("invalid")
    
    def test_invalid_unit(self):
        """Test that invalid unit raises error."""
        with pytest.raises(ValueError, match="Invalid unit"):
            CustomTimeframe("5x")
    
    def test_zero_value(self):
        """Test that zero value raises error."""
        with pytest.raises(ValueError, match="Value must be positive"):
            CustomTimeframe("0m")
    
    def test_negative_value(self):
        """Test that negative value raises error."""
        with pytest.raises(ValueError, match="Value must be positive"):
            CustomTimeframe("-1m")
    
    def test_invalid_value_type(self):
        """Test that invalid value type raises error."""
        with pytest.raises(ValueError, match="Invalid timeframe string"):
            CustomTimeframe("abc5m")


class TestCustomTimeframeProperties:
    """Test CustomTimeframe properties and methods."""
    
    def test_minutes_property_minutes(self):
        """Test minutes property for minutes."""
        tf = CustomTimeframe("5m")
        assert tf.minutes == 5
    
    def test_minutes_property_hours(self):
        """Test minutes property for hours."""
        tf = CustomTimeframe("2h")
        assert tf.minutes == 120
    
    def test_minutes_property_days(self):
        """Test minutes property for days."""
        tf = CustomTimeframe("1d")
        assert tf.minutes == 1440
    
    def test_minutes_property_weeks(self):
        """Test minutes property for weeks."""
        tf = CustomTimeframe("1w")
        assert tf.minutes == 10080
    
    def test_minutes_property_months(self):
        """Test minutes property for months."""
        tf = CustomTimeframe("1M")
        assert tf.minutes == 43200  # 30 days
    
    def test_minutes_property_years(self):
        """Test minutes property for years."""
        tf = CustomTimeframe("1y")
        assert tf.minutes == 525600  # 365 days
    
    def test_pandas_offset_minutes(self):
        """Test pandas offset for minutes."""
        tf = CustomTimeframe("5m")
        assert tf.to_pandas_offset() == "5min"
    
    def test_pandas_offset_hours(self):
        """Test pandas offset for hours."""
        tf = CustomTimeframe("2h")
        assert tf.to_pandas_offset() == "2H"
    
    def test_pandas_offset_days(self):
        """Test pandas offset for days."""
        tf = CustomTimeframe("1d")
        assert tf.to_pandas_offset() == "1D"
    
    def test_pandas_offset_weeks(self):
        """Test pandas offset for weeks."""
        tf = CustomTimeframe("1w")
        assert tf.to_pandas_offset() == "1W"
    
    def test_pandas_offset_months(self):
        """Test pandas offset for months."""
        tf = CustomTimeframe("3M")
        assert tf.to_pandas_offset() == "3M"
    
    def test_pandas_offset_years(self):
        """Test pandas offset for years."""
        tf = CustomTimeframe("1y")
        assert tf.to_pandas_offset() == "1Y"


class TestCustomTimeframeEquality:
    """Test CustomTimeframe equality and hashing."""
    
    def test_equality_same_values(self):
        """Test that same values are equal."""
        tf1 = CustomTimeframe("5m")
        tf2 = CustomTimeframe("5m")
        assert tf1 == tf2
    
    def test_equality_different_values(self):
        """Test that different values are not equal."""
        tf1 = CustomTimeframe("5m")
        tf2 = CustomTimeframe("10m")
        assert tf1 != tf2
    
    def test_equality_different_units(self):
        """Test that different units are not equal."""
        tf1 = CustomTimeframe("5m")
        tf2 = CustomTimeframe("5h")
        assert tf1 != tf2
    
    def test_hash_consistency(self):
        """Test that hash is consistent."""
        tf1 = CustomTimeframe("5m")
        tf2 = CustomTimeframe("5m")
        assert hash(tf1) == hash(tf2)
    
    def test_set_operations(self):
        """Test that CustomTimeframe works in sets."""
        timeframes = {
            CustomTimeframe("1m"),
            CustomTimeframe("5m"),
            CustomTimeframe("1h"),
            CustomTimeframe("1d"),
        }
        assert len(timeframes) == 4
        assert CustomTimeframe("1m") in timeframes


class TestCustomTimeframePydanticIntegration:
    """Test CustomTimeframe integration with Pydantic."""
    
    def test_pydantic_validation(self):
        """Test that Pydantic validation works."""
        tf = CustomTimeframe("5m")
        # Should not raise any validation errors
        assert tf.value == 5
        assert tf.unit == TimeframeUnit.MINUTE
    
    def test_pydantic_serialization(self):
        """Test that Pydantic serialization works."""
        tf = CustomTimeframe("5m")
        data = tf.model_dump()
        assert data["value"] == 5
        assert data["unit"] == "minute"
    
    def test_pydantic_deserialization(self):
        """Test that Pydantic deserialization works."""
        data = {"value": 5, "unit": "minute"}
        tf = CustomTimeframe.model_validate(data)
        assert tf.value == 5
        assert tf.unit == TimeframeUnit.MINUTE
        assert str(tf) == "5m"


class TestCustomTimeframeEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_large_values(self):
        """Test with large values."""
        tf = CustomTimeframe("9999m")
        assert tf.value == 9999
        assert tf.unit == TimeframeUnit.MINUTE
        assert tf.minutes == 9999
    
    def test_single_digit(self):
        """Test with single digit values."""
        tf = CustomTimeframe("1m")
        assert tf.value == 1
        assert tf.unit == TimeframeUnit.MINUTE
    
    def test_double_digit(self):
        """Test with double digit values."""
        tf = CustomTimeframe("15m")
        assert tf.value == 15
        assert tf.unit == TimeframeUnit.MINUTE
    
    def test_repr_format(self):
        """Test the repr format."""
        tf = CustomTimeframe("5m")
        assert repr(tf) == "CustomTimeframe(5, minute)" 