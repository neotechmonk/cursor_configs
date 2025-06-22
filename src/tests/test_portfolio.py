"""Tests for portfolio implementations."""

from decimal import Decimal

import pytest

from core.portfolio import SimplePortfolio
from core.protocols import Position


@pytest.fixture
def portfolio():
    return SimplePortfolio(
        name="test_portfolio",
        initial_capital=Decimal("100000"),
        risk_limits={
            "max_position_size": Decimal("10000"),
            "max_drawdown": Decimal("0.1"),
        }
    )


def test_portfolio_initialization(portfolio):
    assert portfolio.name == "test_portfolio"
    assert portfolio.initial_capital == Decimal("100000")
    assert portfolio.current_capital == Decimal("100000")
    assert len(portfolio.positions) == 0


def test_portfolio_update_position(portfolio):
    # Add a position
    position = Position(
        symbol="AAPL",
        quantity=Decimal("10"),
        entry_price=Decimal("150"),
        current_price=Decimal("150"),
        unrealized_pnl=Decimal("0"),
        realized_pnl=Decimal("0")
    )
    portfolio.positions["AAPL"] = position
    
    # Update position
    portfolio.update_position("AAPL", Decimal("160"))
    
    assert portfolio.positions["AAPL"].current_price == Decimal("160")
    assert portfolio.positions["AAPL"].unrealized_pnl == Decimal("100")


def test_portfolio_can_open_position(portfolio):
    # Test valid position
    assert portfolio.can_open_position(
        symbol="AAPL",
        quantity=Decimal("10"),
        price=Decimal("150")
    )
    
    # Test position too large
    assert not portfolio.can_open_position(
        symbol="AAPL",
        quantity=Decimal("100"),
        price=Decimal("150")
    )
    
    # Test insufficient capital
    assert not portfolio.can_open_position(
        symbol="AAPL",
        quantity=Decimal("1000"),
        price=Decimal("150")
    )


def test_portfolio_drawdown_limit(portfolio):
    # Add a position with unrealized loss
    position = Position(
        symbol="AAPL",
        quantity=Decimal("100"),
        entry_price=Decimal("150"),
        current_price=Decimal("100"),  # $50 loss per share
        unrealized_pnl=Decimal("-5000"),
        realized_pnl=Decimal("0")
    )
    portfolio.positions["AAPL"] = position
    
    # Test position within drawdown limit
    assert portfolio.can_open_position(
        symbol="MSFT",
        quantity=Decimal("10"),
        price=Decimal("150")
    )
    
    # Add more loss to exceed drawdown limit
    position.unrealized_pnl = Decimal("-15000")
    
    # Test position exceeding drawdown limit
    assert not portfolio.can_open_position(
        symbol="MSFT",
        quantity=Decimal("10"),
        price=Decimal("150")
    ) 