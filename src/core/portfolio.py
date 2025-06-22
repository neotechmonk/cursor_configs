"""Portfolio management implementation."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict

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
        self.current_capital = self.initial_capital
    
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