"""Portfolio protocol definitions."""

from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from core.sessions.protocols import TradingSessionProtocol


@runtime_checkable
class PortfolioProtocol(Protocol):
    """Protocol for portfolio implementations."""
    
    @property
    def name(self) -> str:
        """Get portfolio name."""
        ...
    @property
    def initial_capital(self) -> Decimal:
        """Get portfolio initial capital."""
        ...

    def get_current_equity(self) -> Decimal:
        """Get current equity."""
        ...
    
    def can_open_position(self, symbol: str, quantity: Decimal, price: Decimal) -> bool:
        """Check if portfolio can open a new position."""
        ...
    
    def get_realised_pnl(self) -> Decimal:
        """Get realised P&L."""
        ...
    
    def get_unrealised_pnl(self) -> Decimal:
        """Get unrealised P&L."""
        ...
    
    def get_open_sessions(self) -> list["TradingSessionProtocol"]:
        """Get all Trading sessions."""
        ...
    
    def get_all_sessions(self) -> list["TradingSessionProtocol"]:
        """Get all Trading sessions."""
        ...


