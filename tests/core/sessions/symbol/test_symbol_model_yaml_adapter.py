import textwrap
from pathlib import Path

import pytest

from core.sessions.symbol_config.adapter import SymbolYamlAdapter
from core.sessions.symbol_config.model import RawSymbolConfig
from core.shared.config import ConfigPersistenceAdapterProtocol


# --- Test fixtures ------------------------------------------------------------
@pytest.fixture
def symbols_yaml_min(tmp_path: Path) -> Path:
    """YAML containing a single symbol (AAPL)."""
    yaml_text = textwrap.dedent(
        """
        symbols:
          AAPL:
            providers:
              data: csv
              execution: ib
            timeframe: "5m"
            enabled: true
            strategy: breakout
        """
    )
    path = tmp_path / "symbols.yaml"
    path.write_text(yaml_text, encoding="utf-8")
    return path


@pytest.fixture
def symbols_yaml_multi(tmp_path: Path) -> Path:
    """YAML containing two symbols (AAPL, MSFT)."""
    yaml_text = textwrap.dedent(
        """
        symbols:
          AAPL:
            providers: { data: csv, execution: ib }
            timeframe: "5m"
            enabled: true
            strategy: breakout
          MSFT:
            providers: { data: csv, execution: ib }
            timeframe: "1d"
            enabled: true
            strategy: trend-following
        """
    )
    path = tmp_path / "symbols.yaml"
    path.write_text(yaml_text, encoding="utf-8")
    return path


# --- Tests: get / get_all / cache --------------------------------------------
def test_yaml_symbol_adapter_get_respects_protocol(symbols_yaml_min: Path) -> None:
    adapter: ConfigPersistenceAdapterProtocol[str, RawSymbolConfig] = SymbolYamlAdapter(path=symbols_yaml_min)

    # Optional runtime assertion if your protocol is @runtime_checkable
    assert isinstance(adapter, ConfigPersistenceAdapterProtocol)

    raw = adapter.get("AAPL")
    assert isinstance(raw, RawSymbolConfig)
    assert raw.symbol == "AAPL"
    assert raw.providers["data"] == "csv"
    assert raw.providers["execution"] == "ib"
    assert raw.timeframe == "5m"
    assert raw.enabled is True
    assert raw.strategy == "breakout"


def test_yaml_symbol_adapter_get_all_respects_protocol(symbols_yaml_multi: Path) -> None:
    adapter: ConfigPersistenceAdapterProtocol[str, RawSymbolConfig] = SymbolYamlAdapter(path=symbols_yaml_multi)

    raws = adapter.get_all()
    assert all(isinstance(r, RawSymbolConfig) for r in raws)
    assert {r.symbol for r in raws} == {"AAPL", "MSFT"}

