
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from core.data_provider.protocol import DataProviderProtocol
from core.execution_provider.protocol import ExecutionProviderProtocol
from core.sessions.symbol import RawSymbolConfig, SymbolConfigModel
from core.shared.protocols.service import ReadOnlyServiceProtocol
from core.strategy.protocol import StrategyProtocol


@dataclass(slots=True)
class YamlSymbolAdapter:
    """Implements ReadOnlyServiceProtocol[str, RawSymbolConfig]."""
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
class SymbolTransformer:
    data_service: ReadOnlyServiceProtocol[str, DataProviderProtocol]
    exec_service: ReadOnlyServiceProtocol[str, ExecutionProviderProtocol]
    strategy_service: ReadOnlyServiceProtocol[str, StrategyProtocol]

    def __call__(self, raw: RawSymbolConfig) -> SymbolConfigModel:
        data_provider = self.data_service.get(raw.providers["data"])
        exec_provider = self.exec_service.get(raw.providers["execution"])
        strategy = self.strategy_service.get(raw.strategy)
        if data_provider is None or exec_provider is None or strategy is None:
            raise ValueError("Symbol resolution failed: one or more dependencies missing")
        return SymbolConfigModel(
            symbol=raw.symbol,
            timeframe=raw.timeframe,
            enabled=raw.enabled,
            data_provider=data_provider,
            execution_provider=exec_provider,
            strategy=strategy,
        )