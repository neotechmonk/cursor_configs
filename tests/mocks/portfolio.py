from dataclasses import dataclass
from decimal import Decimal


@dataclass
class MockPortfolio:
    """Mock portfolio that implements PortfolioProtocol."""
    name: str = "main_account"
    
    @property
    def initial_capital(self) -> Decimal:
        return Decimal("10000.0")
    
    def get_current_equity(self) -> Decimal:
        return Decimal("10000.0")
    
    def can_open_position(self, symbol: str, quantity: Decimal, price: Decimal) -> bool:
        return True
    
    def get_realised_pnl(self) -> Decimal:
        return Decimal("0.0")
    
    def get_unrealised_pnl(self) -> Decimal:
        return Decimal("0.0")
    
    def get_open_sessions(self) -> list:
        return []
    
    def get_all_sessions(self) -> list:
        return []