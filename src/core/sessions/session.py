from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

from core.portfolio.protocol import PortfolioProtocol
from core.sessions.protocols import TradingSessionProtocol
from core.sessions.symbol import (
    RawSymbolConfig,
    SymbolConfigModel,
    resolve_symbol_config_from_raw_model,
)
from util.yaml_config_loader import load_yaml_config


class TradingSessionSettings(BaseSettings):
    model_config = ConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False
    )
    config_dir: Path = Path("configs/sessions")


class TradingSessionConfig(BaseModel):
    """Session configuration."""
    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
    )
    name: str
    description: Optional[str] = None
    portfolio: PortfolioProtocol
    capital_allocation: float
    # strategies: List[str]
    symbols: Dict[str, SymbolConfigModel]


class RawSessionConfig(BaseModel):
    name: str
    description: Optional[str] = None
    portfolio: str
    capital_allocation: Decimal
    symbols: Dict[str, RawSymbolConfig] 


def parse_raw_session_config(raw_dict: dict) -> RawSessionConfig:
    raw_session = RawSessionConfig(**raw_dict)

    # Inject symbol names into each RawSymbolConfig
    updated_symbols = {
        sym_name: raw_session.symbols[sym_name].model_copy(update={"symbol": sym_name})
        for sym_name in raw_session.symbols.keys()
    }

    return raw_session.model_copy(update={"symbols": updated_symbols})


def resolve_session_config(
    raw: RawSessionConfig,
    data_provider_service,
    execution_provider_service,
    portfolio_service
) -> TradingSessionConfig:
    resolved_symbols = {
        symbol_name: resolve_symbol_config_from_raw_model(
            raw_cfg,
            data_provider_service,
            execution_provider_service
        )
        for symbol_name, raw_cfg in raw.symbols.items()
    }

    return TradingSessionConfig(
        name=raw.name,
        description=raw.description,
        portfolio=portfolio_service.get(raw.portfolio),
        capital_allocation=raw.capital_allocation,
        symbols=resolved_symbols
    )


@dataclass
class TradingSessionService:
    """Service Layer: Business logic for trading session operations."""
    sessions_dir: Path
    data_provider_service: Any
    execution_provider_service: Any
    portfolio_service: Any

    _session_cache: Dict[str, TradingSessionProtocol] = field(default_factory=dict, init=False)

    def get(self, name: str) -> TradingSessionProtocol:
        """Get trading session by name - honors TradingSessionServiceProtocol."""
        if name in self._session_cache:
            return self._session_cache[name]

        session_config = self._load_session_config(name)
        session = self._build_trading_session(session_config)
        self._session_cache[name] = session
        return session

    def get_all(self) -> List[TradingSessionProtocol]:
        """Get all trading sessions - honors TradingSessionServiceProtocol."""
        sessions = []
        for config_file in self.sessions_dir.glob("*.yaml"):
            session_name = config_file.stem
            sessions.append(self.get(session_name))
        return sessions

    def _load_session_config(self, session_name: str) -> TradingSessionConfig:
        config_path = self.sessions_dir / f"{session_name}.yaml"
        raw_dict = load_yaml_config(config_path)
        raw_config = parse_raw_session_config(raw_dict)
        return resolve_session_config(
            raw_config,
            self.data_provider_service,
            self.execution_provider_service,
            self.portfolio_service
        )

    def _build_trading_session(self, config: TradingSessionConfig) -> "TradingSession":
        """Construct a TradingSession with explicit config unpacking."""
        return TradingSession(
            name=config.name,
            portfolio=config.portfolio,
            capital_allocation=Decimal(str(config.capital_allocation)),
            symbols=config.symbols
        )
    

class TradingSession:
    """Trading session implementation."""

    def __init__(
        self,
        name: str,
        portfolio: PortfolioProtocol,
        capital_allocation: Decimal,
        symbols: Dict[str, SymbolConfigModel],
    ):
        self._name = name
        self._portfolio = portfolio
        self._capital_allocation = capital_allocation
        self._symbols = symbols
        self._session_pnl = Decimal("0.0")

    @property
    def name(self) -> str:
        return self._name

    @property
    def portfolio(self) -> PortfolioProtocol:
        return self._portfolio

    @property
    def capital_allocation(self) -> Decimal:
        return self._capital_allocation

    def get_symbol_config(self, symbol: str) -> SymbolConfigModel:
        if symbol not in self._symbols:
            raise ValueError(f"Symbol '{symbol}' not found in session '{self._name}'")
        return self._symbols[symbol]

    def is_symbol_enabled(self, symbol: str) -> bool:
        config = self.get_symbol_config(symbol)
        return config.enabled

    def get_enabled_symbols(self) -> List[str]:
        return [s for s, cfg in self._symbols.items() if cfg.enabled]

    def get_price_data(self, symbol: str) -> pd.DataFrame:
        config = self.get_symbol_config(symbol)
        if not config.enabled:
            raise ValueError(f"Symbol '{symbol}' is disabled in session '{self._name}'")
        return config.data_provider.get_price_data(symbol, config.timeframe)

    def update_session_pnl(self, pnl: Decimal) -> None:
        self._session_pnl = pnl

    def get_session_pnl(self) -> Decimal:
        return self._session_pnl