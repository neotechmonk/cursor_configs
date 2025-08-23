# tests/test_symbols_container_happy.py
from __future__ import annotations

from unittest.mock import Mock
import pytest

from dependency_injector import providers

from core.sessions.symbol_config.container import SymbolsContainer  # path to your container


def test_symbols_container_happy_path_with_dict_adapter():
    """
    Happy path: use dict adapter, provide a symbols mapping, and ensure the
    service wires correctly and invokes the transformer for get() and get_all().
    """

    # --- Arrange -------------------------------------------------------------
    # Minimal raw symbols mapping exactly as your YAML 'symbols:' block would look.
    raw_symbols = {
        "AAPL": {
            "strategy": "sample_strategy",
            "providers": {"data": "csv", "execution": "file"},
            "timeframe": "5m",
            "enabled": True,
        },
        "SPY": {
            "strategy": "sample_strategy",
            "providers": {"data": "yahoo", "execution": "file"},
            "timeframe": "1d",
            "enabled": True,
        },
    }

    # Build container
    c = SymbolsContainer()

    # Select the dict adapter
    c.config.adapter.kind.override("dict")

    # No cache
    c.cache.override(providers.Object(None))

    # Provide the mapping that the dict adapter will read from
    c.symbols_mapping.override(raw_symbols)

    # Mock the transformer so we only test orchestration (not model details)
    transformer_mock = Mock(side_effect=lambda raw: ("SYMBOL_CONFIG", getattr(raw, "symbol", None)))
    c.transformer.override(providers.Object(transformer_mock))

    # Optional: inject a cache mock if you want to assert read-through later
    # cache_mock = Mock()
    # c.cache.override(cache_mock)

    svc = c.service()

    # --- Act ----------------------------------------------------------------
    out_single = svc.get("AAPL")          # should invoke adapter.get + transformer once
    out_all = list(svc.get_all())         # should invoke adapter.get_all + transformer for each item

    # --- Assert --------------------------------------------------------------
    # The transformer should have been called once for get() and once per symbol for get_all()
    # Total symbols = 2, so total calls = 1 (get) + 2 (get_all) = 3
    assert transformer_mock.call_count == 3

    # Check outputs are what the transformer returned
    assert out_single == ("SYMBOL_CONFIG", "AAPL")
    # get_all order may follow dict order; convert to a set of results
    assert set(out_all) == {("SYMBOL_CONFIG", "AAPL"), ("SYMBOL_CONFIG", "SPY")}