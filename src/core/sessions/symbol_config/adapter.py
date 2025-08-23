
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional

import yaml

from core.sessions.symbol_config.model import RawSymbolConfig


@dataclass(slots=True)
class SymbolYamlAdapter:
    """Implements ConfigPersistenceAdapterProtocol[str, RawSymbolConfig]."""
    path: Path
    _blob: dict = field(init=False)

    def __post_init__(self):
        with self.path.open(encoding="utf-8") as f:
            self._blob = yaml.safe_load(f) or {}
        if "symbols" not in self._blob or not isinstance(self._blob["symbols"], dict):
            self._blob["symbols"] = {}

    def get(self, key: str) -> RawSymbolConfig:
        try:
            node = dict(self._blob["symbols"][key])  # shallow copy
        except KeyError as e:
            raise KeyError(f"symbol '{key}' not found in {self.path}") from e
        node.setdefault("symbol", key)
        return RawSymbolConfig(**node)

    def get_all(self) -> list[RawSymbolConfig]:
        out: list[RawSymbolConfig] = []
        for sym, cfg in self._blob["symbols"].items():
            node = dict(cfg)
            node.setdefault("symbol", sym)
            out.append(RawSymbolConfig(**node))
        return out

@dataclass(slots=True)
class SymbolDictAdapter:
    """Read-only adapter over the session's symbols mapping.
    Used case : nested Symbol configs in the TradingSession config. 
    Session will have the symbols as dict after parsing the outer contenet
    E.g.
        {
            "AAPL": {
                "strategy": "sample_strategy",
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "5m",
                "enabled": true
            }
        }
    """
    symbols: Mapping[str, dict] = field(init=False)

    def get(self, key: str) -> Optional[RawSymbolConfig]:
        d = self.symbols.get(key)
        if not d:
            return None
        return RawSymbolConfig(symbol=key, **d)

    def get_all(self) -> Iterable[RawSymbolConfig]:
        return [RawSymbolConfig(symbol=k, **v) for k, v in self.symbols.items()]