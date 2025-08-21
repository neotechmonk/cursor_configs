
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from core.sessions.symbol_config import RawSymbolConfig


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

