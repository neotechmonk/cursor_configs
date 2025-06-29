"""Time-related classes for the trading system."""

import re
from collections import namedtuple
from datetime import datetime, timedelta
from enum import Enum
from typing import Union, overload

from pydantic import BaseModel, model_validator

TimeframeMeta = namedtuple("TimeframeMeta", ["label", "short", "offset", "minutes"])


class TimeframeUnit(Enum):
    MINUTE = TimeframeMeta("minute", "m", "min", 1)
    HOUR   = TimeframeMeta("hour", "h", "H", 60)
    DAY    = TimeframeMeta("day", "d", "D", 24 * 60)
    WEEK   = TimeframeMeta("week", "w", "W", 7 * 24 * 60)
    MONTH  = TimeframeMeta("month", "M", "M", 30 * 24 * 60)   # Approximate
    YEAR   = TimeframeMeta("year", "y", "Y", 365 * 24 * 60)   # Approximate

    @property
    def label(self): return self.value.label
    @property
    def short(self): return self.value.short
    @property
    def pandas_offset(self): return self.value.offset
    @property
    def minutes(self): return self.value.minutes

    @classmethod
    def from_short(cls, short_code: str) -> "TimeframeUnit":
        for unit in cls:
            if unit.short == short_code:
                return unit
        raise ValueError(f"Unknown short code: {short_code}")


class CustomTimeframe(BaseModel):
    """Custom timeframe as a Pydantic model with overloaded constructors."""
    model_config = {
        "frozen": True  # Makes the model hashable and immutable
    }
    
    value: int
    unit: TimeframeUnit
    
    # Overloads for type hints
    @overload
    def __init__(self, timeframe_str: str) -> None: ...
    
    @overload
    def __init__(self, value: int, unit: TimeframeUnit) -> None: ...
    
    def __init__(self, value: Union[int, str], unit: TimeframeUnit = None, **kwargs):
        """Initialize with either string ("5m") or value and unit."""
        if isinstance(value, str):
            # Parse string like "5m", "1h", "1d"
            tf = self._from_string(value)
            super().__init__(value=tf["value"], unit=tf["unit"], **kwargs)
        else:
            # Use value and unit directly
            super().__init__(value=value, unit=unit, **kwargs)
    
    @classmethod
    def _from_string(cls, data):
        if isinstance(data, str):
            # Extract numeric part (including sign) and unit part
            match = re.match(r'^(-?\d+)([a-zA-Z]+)$', data)
            if not match:
                raise ValueError(f"Invalid timeframe string: {data}")
            
            val_str, unit_str = match.groups()
            value = int(val_str)

            try:
                unit = TimeframeUnit.from_short(unit_str)
            except ValueError as e:
                raise ValueError(f"Invalid timeframe unit: {unit_str}") from e

            return {"value": value, "unit": unit}

        return data
    
    @model_validator(mode="after")
    def check_value_positive(self):
        if self.value <= 0:
            raise ValueError("Timeframe value must be positive")
        return self

    @property
    def minutes(self) -> int:
        return self.value * self.unit.minutes

    def to_pandas_offset(self) -> str:
        return f"{self.value}{self.unit.pandas_offset}"

    def _to_timedelta(self) -> timedelta:
        return timedelta(minutes=self.minutes)
    
    def __radd__(self, other):
        """Right addition operator for CustomTimeframe.
        
        Allows adding a CustomTimeframe to datetime or timedelta objects.
        
        Examples:
            >>> from datetime import datetime, timedelta
            >>> tf = CustomTimeframe("1h")
            >>> dt = datetime(2024, 1, 1, 12, 0)
            >>> result = dt + tf  # This calls __radd__
            >>> print(result)
            2024-01-01 13:00:00
            
            >>> td = timedelta(minutes=30)
            >>> result = td + tf  # This calls __radd__
            >>> print(result)
            1:30:00
        """
        if isinstance(other, datetime):
            return other + self._to_timedelta()
        if isinstance(other, timedelta):
            return other + self._to_timedelta()
        return NotImplemented
    
    def __add__(self, other):
        """Addition operator for CustomTimeframe.
        
        Allows adding a timedelta to a CustomTimeframe.
        
        Examples:
            >>> from datetime import timedelta
            >>> tf = CustomTimeframe("1h")
            >>> td = timedelta(minutes=30)
            >>> result = tf + td  # This calls __add__
            >>> print(result)
            1:30:00
        """
        if isinstance(other, timedelta):
            return self._to_timedelta() + other
        return NotImplemented

    def __str__(self) -> str:
        return f"{self.value}{self.unit.short}"

    def __repr__(self) -> str:
        return self.__str__()
    
    @classmethod
    def parse_str_input(cls, data):
        if isinstance(data, str):
            val_str = ''.join(filter(str.isdigit, data))
            unit_str = ''.join(filter(str.isalpha, data))

            if not val_str or not unit_str:
                raise ValueError(f"Invalid timeframe string: {data}")

            value = int(val_str)
            if value <= 0:
                raise ValueError("Timeframe value must be positive")

            try:
                unit = TimeframeUnit.from_short(unit_str)
            except ValueError as e:
                raise ValueError(f"Invalid timeframe unit: {unit_str}") from e

            return {"value": value, "unit": unit}

        return data
