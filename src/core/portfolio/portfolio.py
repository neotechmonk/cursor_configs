"""Portfolio management implementation."""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings

from core.portfolio.protocol import PortfolioProtocol
from util.yaml_config_loader import load_yaml_config

if TYPE_CHECKING:
    from core.sessions.protocols import TradingSessionProtocol


class PortfolioSettings(BaseSettings):
    """Portfolio-specific settings from app configuration."""
    model_config = ConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False
    )
    config_dir: Path = Field(default=Path("configs/portfolios"))
    

class PortfolioConfig(BaseModel):
    """Pydantic model for portfolio configuration."""
    model_config = ConfigDict(frozen=True)
    
    name: str = Field(..., min_length=1, description="Portfolio name")
    description: Optional[str] = None
    initial_capital: float = Field(..., gt=0, description="Initial capital amount")
    # risk_limits: Dict[str, float]


class Portfolio(BaseModel):
    """Portfolio implementation with Pydantic validation."""
    model_config = ConfigDict(frozen=True)
    
    name: str = Field(..., min_length=1, description="Portfolio name")
    description: Optional[str] = None
    initial_capital: Decimal = Field(..., gt=0, description="Initial capital amount")
    
    @field_validator('initial_capital', mode='before')
    @classmethod
    def validate_initial_capital(cls, v):
        """Convert float to Decimal and validate."""
        if isinstance(v, float):
            return Decimal(str(v))
        elif isinstance(v, str):
            return Decimal(v)
        return v
    
    def get_current_equity(self) -> Decimal:
        """Get current equity."""
        raise NotImplementedError("Current equity is not implemented in this portfolio.")

    # TODO : need a Position concept. probably in the sessions
    def positions_by_symbol(self) -> Dict[str, Any]:
        """Positions indexed by symbol."""
        raise NotImplementedError("Positions are not implemented in this portfolio.")
   
    def can_open_position(
        self,
        symbol: str,
        quantity: Decimal,
        price: Decimal
    ) -> bool:
        """Check if portfolio can open a new position."""
        raise NotImplementedError("Can open position is not implemented in this portfolio.")
    
    def get_open_sessions(self) -> list["TradingSessionProtocol"]:
        """Get open sessions."""
        raise NotImplementedError("Sessions are not implemented in this portfolio.")
    
    def get_all_sessions(self) -> list["TradingSessionProtocol"]:
        """Get all sessions."""
        raise NotImplementedError("All sessions are not implemented in this portfolio.")
    
    def get_realised_pnl(self) -> Decimal:
        """Get realised P&L."""
        raise NotImplementedError("Realised P&L is not implemented in this portfolio.")
    
    def get_unrealised_pnl(self) -> Decimal:
        """Get unrealised P&L."""
        raise NotImplementedError("Unrealised P&L is not implemented in this portfolio.")

 
# FIXME : make this less greedy by extracting parameters from config
@dataclass
class PortfolioService:
    settings: PortfolioSettings
    cache: Dict[str, PortfolioProtocol]

    def _load_portfolio_by_name(self, name: str) -> PortfolioProtocol:
        path = self.settings.config_dir / f"{name}.yaml"
        config = load_yaml_config(path, PortfolioConfig)
        return Portfolio(name=name, description=config.description, initial_capital=config.initial_capital)

    def get(self, name: str) -> PortfolioProtocol:
        if name not in self.cache:
            self.cache[name] = self._load_portfolio_by_name(name)
        return self.cache[name]

    def get_all(self) -> list[PortfolioProtocol]:
        for file in self.settings.config_dir.glob("*.yaml"):
            name = file.stem
            if name not in self.cache:
                self.cache[name] = self._load_portfolio_by_name(name)
        return list(self.cache.values())

    def clear_cache(self) -> None:
        self.cache.clear()
