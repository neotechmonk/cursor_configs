import pytest

from core.sessions.symbol_config.adapter import SymbolDictAdapter
from core.sessions.symbol_config.model import RawSymbolConfig
from core.shared.config import ConfigPersistenceAdapterProtocol


def test_dict_symbol_adapter_get_respects_protocol() -> None:
    symbols = {
        "AAPL": {
            "providers": {"data": "csv", "execution": "ib"},
            "timeframe": "5m",
            "enabled": True,
            "strategy": "breakout",
        }
    }

    adapter = SymbolDictAdapter()
    adapter.symbols = symbols  # set internal mapping

    assert isinstance(adapter, ConfigPersistenceAdapterProtocol)

    raw = adapter.get("AAPL")
    assert isinstance(raw, RawSymbolConfig)
    assert raw.symbol == "AAPL"
    assert raw.providers["data"] == "csv"
    assert raw.providers["execution"] == "ib"
    assert raw.timeframe == "5m"
    assert raw.enabled is True
    assert raw.strategy == "breakout"


def test_dict_symbol_adapter_get_all_respects_protocol() -> None:
    symbols = {
        "AAPL": {
            "providers": {"data": "csv", "execution": "ib"},
            "timeframe": "5m",
            "enabled": True,
            "strategy": "breakout",
        },
        "MSFT": {
            "providers": {"data": "csv", "execution": "ib"},
            "timeframe": "1d",
            "enabled": True,
            "strategy": "trend-following",
        },
    }

    adapter = SymbolDictAdapter()
    adapter.symbols = symbols

    raws = adapter.get_all()
    assert all(isinstance(r, RawSymbolConfig) for r in raws)
    assert {r.symbol for r in raws} == {"AAPL", "MSFT"}