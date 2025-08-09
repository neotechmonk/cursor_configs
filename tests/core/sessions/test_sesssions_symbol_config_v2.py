# tests/symbol/test_yaml_symbol_adapter_happy.py
import textwrap
from typing import Optional

from core.sessions.symbol import RawSymbolConfig, SymbolConfigModel
from core.sessions.symbolv2 import SymbolTransformer, YamlSymbolAdapter
from core.shared.protocols.config import ReadOnlyConfigService
from core.time import CustomTimeframe
from tests.mocks.providers import MockDataProviderService, MockExecutionProviderService
from tests.mocks.strategies import MockStrategyService


class MockInMemoryCache[K, V]():
    def __init__(self):
        self._d: dict[K, V] = {}
    def get(self, key: K) -> Optional[V]:
        return self._d.get(key)
    def set(self, key: K, value: V) -> None:
        self._d[key] = value
    def clear(self) -> None:
        self._d.clear()


def test_yaml_symbol_adapter_get_and_get_all_happy_path(tmp_path):
    # Arrange: write a minimal valid YAML
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
          MSFT:
            providers:
              data: csv
              execution: ib
            timeframe: "1d"
            enabled: true
            strategy: trend-following
        """
    )
    path = tmp_path / "symbols.yaml"
    path.write_text(yaml_text, encoding="utf-8")

    adapter = YamlSymbolAdapter(path=path)

    # Act
    raw_aapl = adapter.get("AAPL")
    raws = adapter.get_all()

    # Assert single
    assert isinstance(raw_aapl, RawSymbolConfig)
    assert raw_aapl.symbol == "AAPL"
    assert raw_aapl.providers["data"] == "csv"
    assert raw_aapl.providers["execution"] == "ib"
    assert raw_aapl.timeframe == "5m"
    assert raw_aapl.enabled is True
    assert raw_aapl.strategy == "breakout"

    # Assert get_all
    symbols = {r.symbol for r in raws}
    assert symbols == {"AAPL", "MSFT"}


def test_symbol_transformer_happy_path():
    # Arrange
    raw = RawSymbolConfig(
        symbol="AAPL",
        timeframe="5m",
        enabled=True,
        providers={"data": "csv", "execution": "ib"},
        strategy="breakout",
    )

    transformer = SymbolTransformer(
        data_service=MockDataProviderService(),
        exec_service=MockExecutionProviderService(),
        strategy_service=MockStrategyService(),
    )

    # Act
    model = transformer(raw)

    # Assert
    assert isinstance(model, SymbolConfigModel)
    assert model.symbol == "AAPL"
    assert model.timeframe == CustomTimeframe("5m")
    assert model.enabled is True
    assert model.data_provider.name == "csv"
    assert model.execution_provider.name == "ib"
    assert model.strategy.name == "breakout"


def test_symbol_service_happy_path(tmp_path):
    # Arrange: YAML file
    yaml_text = textwrap.dedent(
        """
        symbols:
          AAPL:
            providers: { data: csv, execution: ib }
            timeframe: "5m"
            enabled: true
            strategy: breakout
        """
    )
    path = tmp_path / "symbols.yaml"
    path.write_text(yaml_text, encoding="utf-8")

    adapter = YamlSymbolAdapter(path=path)

    transformer = SymbolTransformer(
        data_service=MockDataProviderService(),
        exec_service=MockExecutionProviderService(),
        strategy_service=MockStrategyService(),
    )

    cache = MockInMemoryCache[str, SymbolConfigModel]()

    service = ReadOnlyConfigService[str, RawSymbolConfig, SymbolConfigModel](
        adapter=adapter,
        transformer=transformer,
        cache=cache,
        cache_namespace="symbol:",
        key_from_target=lambda t: t.symbol,  # primes cache on get_all()
    )

    # Act: first call (miss → adapter+transformer)
    aapl = service.get("AAPL")
    # Act: second call (hit cache)
    aapl_again = service.get("AAPL")

    # Assert model
    assert isinstance(aapl, SymbolConfigModel)
    assert aapl.symbol == "AAPL"
    assert aapl.data_provider.name == "csv"
    assert aapl.execution_provider.name == "ib"
    assert aapl.strategy.name == "breakout"

    # Assert cache effectiveness (same object instance is a simple proxy for cache hit)
    assert aapl_again is aapl

    # Act: get_all primes cache (if more symbols existed)
    all_syms = service.get_all()
    assert len(all_syms) == 1 and all_syms[0].symbol == "AAPL"