"""Tests for Portfolio class implementation."""

from decimal import Decimal
import inspect

import pytest

from core.portfolio.portfolio import Portfolio
from core.portfolio.protocol import PortfolioProtocol


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

def test_portfolio_implements_all_protocol_members():
    """Ensure Portfolio correctly implements PortfolioProtocol.
    
    - Methods must be defined as methods.
    - Properties (including annotated fields) can be satisfied by attributes or properties.
    """

    # --- Methods ---
    protocol_methods = {
        name for name, member in inspect.getmembers(PortfolioProtocol)
        if inspect.isfunction(member)
    }

    portfolio_methods = {
        name for name, member in inspect.getmembers(Portfolio)
        if inspect.isfunction(member)
    }

    missing_methods = protocol_methods - portfolio_methods

    # --- Attributes / Properties ---
    protocol_props = {
        name for name, member in inspect.getmembers(PortfolioProtocol)
        if isinstance(member, property)
    }

    # Add any explicitly annotated attributes on the Protocol
    protocol_props |= set(getattr(PortfolioProtocol, '__annotations__', {}).keys())

    # Portfolio members: allow property or Pydantic field
    portfolio_attrs = {
        name for name, member in inspect.getmembers(Portfolio)
        if not inspect.isroutine(member)  # includes property, descriptor, class var
    }

    # Also include Pydantic model fields (from __annotations__)
    portfolio_attrs |= set(getattr(Portfolio, '__annotations__', {}).keys())

    missing_attrs = protocol_props - portfolio_attrs

    # --- Combined assertion ---
    messages = []
    if missing_methods:
        messages.append(f"Missing methods: {missing_methods}")
    if missing_attrs:
        messages.append(f"Missing properties/attributes: {missing_attrs}")

    assert not messages, "Portfolio is missing protocol members:\n" + "\n".join(messages)