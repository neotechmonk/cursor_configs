from decimal import Decimal

import pandas as pd
import pytest
from pydantic import ValidationError

from core.order.models import Order, OrderSide, OrderType

# ----------------------------
# Happy Path Tests
# ----------------------------


def test_valid_market_buy_order():
    order = Order(
        symbol="BTCUSD",
        timeframe="1m",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("0.01"),
        entry_price=Decimal("30000"),
        stop_price=Decimal("29000"),
        target_price=Decimal("31000"),
        tag="strategy_a",
        placement_bar_index=pd.Timestamp("2023-01-01 00:00:00"),
        ttl_bars=10
    )
    assert order.side == OrderSide.BUY


def test_valid_limit_sell_order():
    order = Order(
        symbol="ETHUSD",
        timeframe="5m",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("2"),
        entry_price=Decimal("2000"),
        stop_price=Decimal("2100"),
        target_price=Decimal("1900"),
    )
    assert order.order_type == OrderType.LIMIT


# ----------------------------
# Validation Error Tests
# ----------------------------

def test_buy_order_invalid_stop_price():
    with pytest.raises(ValidationError) as exc:
        Order(
            symbol="BTCUSD",
            timeframe="1m",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.5"),
            entry_price=Decimal("30000"),
            stop_price=Decimal("31000"),  # Invalid: stop >= entry
            target_price=Decimal("39000")
        )
    errors = str(exc.value)
    assert "Stop price must be less than entry price" in errors


def test_buy_order_invalid_target_price():
    with pytest.raises(ValidationError) as exc:
        Order(
            symbol="BTCUSD",
            timeframe="1m",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.5"),
            entry_price=Decimal("30000"),
            stop_price=Decimal("29000"),  
            target_price=Decimal("29000")  # Invalid: target <= entry
        )
    errors = str(exc.value)
    assert "Target price must be greater than entry price for buy orders" in errors


def test_sell_order_invalid_stop_price():
    with pytest.raises(ValidationError) as exc:
        Order(
            symbol="ETHUSD",
            timeframe="1m",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=Decimal("1"),
            entry_price=Decimal("2000"),
            stop_price=Decimal("1900"),
            target_price=Decimal("1900")
        )
    errors = str(exc.value)
    assert "Stop price must be greater than entry price" in errors


def test_sell_order_invalid_target_price():
    with pytest.raises(ValidationError) as exc:
        Order(
            symbol="ETHUSD",
            timeframe="1m",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=Decimal("1"),
            entry_price=Decimal("2000"),
            stop_price=Decimal("2100"),
            target_price=Decimal("2100")
        )
    errors = str(exc.value)
    assert "Target price must be less than entry price" in errors


def test_invalid_ttl_bars():
    with pytest.raises(ValidationError) as exc:
        Order(
            symbol="BTCUSD",
            timeframe="1m",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
            entry_price=Decimal("30000"),
            stop_price=Decimal("29000"),
            target_price=Decimal("31000"),
            ttl_bars=0  # Invalid: must be ≥ 1
        )
    assert "Input should be greater than or equal to 1 " in str(exc.value)
