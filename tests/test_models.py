import pytest

from models import Direction, PriceLabel


def test_direction_enum():
    assert Direction.UP.value == 1
    assert Direction.DOWN.value == 2
    assert Direction.RANGE.value == 3


def test_price_label_enum():
    assert PriceLabel.OPEN.value == "Open"
    assert PriceLabel.HIGH.value == "High"
    assert PriceLabel.LOW.value == "Low"
    assert PriceLabel.CLOSE.value == "Close"
