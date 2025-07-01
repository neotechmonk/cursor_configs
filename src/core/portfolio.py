"""Portfolio management implementation."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List

from .protocols import Position


@dataclass
class SimplePortfolio:
    """Simple portfolio implementation."""
    
    name: str
    initial_capital: Decimal
    risk_limits: Dict[str, Decimal]
    positions: Dict[str, Position] = field(default_factory=dict)
    current_capital: Decimal = field(init=False)
    
    def __post_init__(self):
        # Ensure current_capital is always a Decimal
        if isinstance(self.initial_capital, float):
            self.current_capital = Decimal(str(self.initial_capital))
        else:
            self.current_capital = self.initial_capital
    
    @property
    def positions_by_symbol(self) -> Dict[str, Position]:
        """Positions indexed by symbol."""
        return self.positions
    
    def update_position(self, symbol: str, price: Decimal) -> None:
        """Update position with new price."""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        position.current_price = price
        position.unrealized_pnl = (
            (price - position.entry_price) * position.quantity
        )
    
    def can_open_position(
        self,
        symbol: str,
        quantity: Decimal,
        price: Decimal
    ) -> bool:
        """Check if portfolio can open a new position."""
        # Check position size limit
        position_value = quantity * price
        if position_value > self.risk_limits["max_position_size"]:
            return False
        
        # Check if we have enough capital
        if position_value > self.current_capital:
            return False
        
        # Check drawdown limit
        total_value = self.current_capital + sum(
            p.unrealized_pnl for p in self.positions.values()
        )
        if total_value < self.initial_capital * (1 - self.risk_limits["max_drawdown"]):
            return False
        
        return True
    
    def get_total_pnl(self) -> Decimal:
        """Get total portfolio P&L (realized + unrealized)."""
        total_pnl = Decimal("0")
        for position in self.positions.values():
            total_pnl += position.realized_pnl + position.unrealized_pnl
        return total_pnl
    
    def get_current_capital(self) -> Decimal:
        """Get current portfolio capital including P&L."""
        return self.current_capital + self.get_total_pnl() 