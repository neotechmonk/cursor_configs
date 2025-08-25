from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

from core.data_provider.service import DataProviderService
from core.execution_provider.service import ExecutionProviderService
from core.portfolio.portfolio import PortfolioService
from core.portfolio.protocol import PortfolioProtocol
from core.sessions.protocols import TradingSessionProtocol
from core.sessions.symbol_config.adapter import SymbolDictAdapter
from core.sessions.symbol_config.model import RawSymbolConfig, SymbolConfigModel
from core.sessions.symbol_config.transformer import SymbolTransformer
from core.shared.config import ReadOnlyConfigService
from core.shared.service import ReadOnlyServiceProtocol
from core.strategy.service import StrategyService
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
    symbols: List[SymbolConfigModel]


class RawSessionConfig(BaseModel):
    name: str
    description: Optional[str] = None
    portfolio: str
    capital_allocation: Decimal
    symbols: Dict[str, dict] 



def resolve_session_config(
    raw: RawSessionConfig,
    data_provider_service: DataProviderService,
    execution_provider_service: ExecutionProviderService,
    portfolio_service: PortfolioService,
    strategy_service: StrategyService
) -> TradingSessionConfig:
    
    symbols_service = ReadOnlyConfigService[str, RawSymbolConfig, SymbolConfigModel](
        adapter=SymbolDictAdapter(symbols=raw.symbols),
        transformer=SymbolTransformer(
            data_service=data_provider_service,
            exec_service=execution_provider_service,
            strategy_service=strategy_service
        ),
        cache=None
    )

    resolved_symbols = symbols_service.get_all()

    # Validate portfolio resolution
    portfolio = portfolio_service.get(raw.portfolio)
    if portfolio is None:
        raise ValueError(f"Error resolving session config: portfolio '{raw.portfolio}' not found")

    return TradingSessionConfig(
        name=raw.name,
        description=raw.description,
        portfolio=portfolio,
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
    strategy_service: Any

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
        
        # Create raw session config and inject symbol names inline
        raw_config = RawSessionConfig(**raw_dict)
        updated_symbols = {
            sym_name: {**raw_config.symbols[sym_name], "symbol": sym_name}
            for sym_name in raw_config.symbols.keys()
        }
        raw_config = raw_config.model_copy(update={"symbols": updated_symbols})
        
        return resolve_session_config(
            raw_config,
            self.data_provider_service,
            self.execution_provider_service,
            self.portfolio_service,
            self.strategy_service
        )
    

    def _build_trading_session(self, config: TradingSessionConfig) -> "TradingSession":
        """Construct a TradingSession with explicit config unpacking."""
        # Convert list of symbols back to dict for TradingSession constructor
        symbols_dict = {symbol.symbol: symbol for symbol in config.symbols}
        
        return TradingSession(
            name=config.name,
            portfolio=config.portfolio,
            capital_allocation=Decimal(str(config.capital_allocation)),
            symbols=symbols_dict
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