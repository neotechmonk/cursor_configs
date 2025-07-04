"""Tests for Portfolio class implementation."""

from decimal import Decimal

import pytest

from core.portfolio.portfolio import Portfolio


def test_portfolio_basic_creation():
    """Test basic portfolio creation."""
    portfolio = Portfolio(
        name="Test Portfolio",
        description="A test portfolio",
        initial_capital=10000.0
    )
    
    assert portfolio.name == "Test Portfolio"
    assert portfolio.description == "A test portfolio"
    assert portfolio.initial_capital == Decimal("10000.0")


def test_portfolio_initial_capital_conversion():
    """Test initial capital conversion from different types."""
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_capital="7500.50"
    )
    
    assert portfolio.initial_capital == Decimal("7500.50")


# Pending methods - marked as xfail
@pytest.mark.xfail(reason="get_current_equity not implemented")
def test_get_current_equity():
    """Test get_current_equity method."""
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_capital=10000.0
    )
    
    equity = portfolio.get_current_equity()
    assert isinstance(equity, Decimal)


@pytest.mark.xfail(reason="positions_by_symbol not implemented")
def test_positions_by_symbol():
    """Test positions_by_symbol method."""
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_capital=10000.0
    )
    
    positions = portfolio.positions_by_symbol()
    assert isinstance(positions, dict)


@pytest.mark.xfail(reason="can_open_position not implemented")
def test_can_open_position():
    """Test can_open_position method."""
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_capital=10000.0
    )
    
    can_open = portfolio.can_open_position(
        symbol="AAPL",
        quantity=Decimal("100"),
        price=Decimal("150.0")
    )
    assert isinstance(can_open, bool)


@pytest.mark.xfail(reason="get_sessions not implemented")
def test_get_sessions():
    """Test get_sessions method."""
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_capital=10000.0
    )
    
    sessions = portfolio.get_sessions()
    assert isinstance(sessions, list)


@pytest.mark.xfail(reason="get_realised_pnl not implemented")
def test_get_realised_pnl():
    """Test get_realised_pnl method."""
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_capital=10000.0
    )
    
    realised_pnl = portfolio.get_realised_pnl()
    assert isinstance(realised_pnl, Decimal)


@pytest.mark.xfail(reason="get_unrealised_pnl not implemented")
def test_get_unrealised_pnl():
    """Test get_unrealised_pnl method."""
    portfolio = Portfolio(
        name="Test Portfolio",
        initial_capital=10000.0
    )
    
    unrealised_pnl = portfolio.get_unrealised_pnl()
    assert isinstance(unrealised_pnl, Decimal) 