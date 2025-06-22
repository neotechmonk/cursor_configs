"""Loader for risk management configuration."""

from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel


class RiskLimits(BaseModel):
    """Risk limits configuration."""
    max_position_size: float
    max_drawdown: float
    stop_loss_pct: float
    take_profit_pct: float


class PositionSizing(BaseModel):
    """Position sizing rules."""
    max_risk_per_trade: float
    max_correlation: float
    max_sector_exposure: float


class PortfolioConstraints(BaseModel):
    """Portfolio constraints."""
    max_leverage: float
    min_liquidity: float
    max_slippage: float


class RiskMonitoring(BaseModel):
    """Risk monitoring settings."""
    check_interval: str
    alert_threshold: float
    max_open_positions: int


class RiskConfig(BaseModel):
    """Complete risk management configuration."""
    default_risk_limits: RiskLimits
    position_sizing: PositionSizing
    portfolio_constraints: PortfolioConstraints
    risk_monitoring: RiskMonitoring


class RiskConfigLoader:
    """Loader for risk management configuration."""
    
    def __init__(self, config_path: Path):
        """Initialize the loader."""
        self.config_path = config_path
        self.config: Optional[RiskConfig] = None
    
    def load(self) -> RiskConfig:
        """Load the configuration from file."""
        with open(self.config_path) as f:
            config_dict = yaml.safe_load(f)
        self.config = RiskConfig.model_validate(config_dict)
        return self.config
    
    def get_risk_limits(self) -> Dict[str, float]:
        """Get risk limits as a dictionary."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        return self.config.default_risk_limits.model_dump()
    
    def get_position_sizing(self) -> Dict[str, float]:
        """Get position sizing rules as a dictionary."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        return self.config.position_sizing.model_dump()
    
    def get_portfolio_constraints(self) -> Dict[str, float]:
        """Get portfolio constraints as a dictionary."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        return self.config.portfolio_constraints.model_dump()
    
    def get_risk_monitoring(self) -> Dict[str, float | str | int]:
        """Get risk monitoring settings as a dictionary."""
        if not self.config:
            raise ValueError("Configuration not loaded")
        return self.config.risk_monitoring.model_dump() 