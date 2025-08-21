# tests/test_read_only_config_service.py
from __future__ import annotations

from dataclasses import dataclass
from typing import (
    cast,
)
from unittest.mock import Mock

from core.shared.config import (
    CacheProtocol,
    ConfigPersistenceAdapterProtocol,
    ReadOnlyConfigService,
)


# --- Tiny domain shapes just for the test ---
@dataclass(frozen=True, slots=True)
class RawModel:
    symbol: str


@dataclass(frozen=True, slots=True)
class TargetModel:
    symbol: str


##--------------------------------
# --- Tests focusing purely on orchestration ---
def test_get_read_through_then_hit_with_protocol_shaped_mocks():
    
    # protocol-shaped adapter mock
    adapter_mock: ConfigPersistenceAdapterProtocol[str, RawModel] = cast(
        ConfigPersistenceAdapterProtocol[str, RawModel],
        Mock(spec=ConfigPersistenceAdapterProtocol)
    )
    # set behavior
    cast(Mock, adapter_mock).get.return_value = RawModel("AAPL")

    # cache & transformer as mocks too
    cache_mock = Mock(spec=CacheProtocol)
    cache_mock.get.return_value = None  # miss on first call

    transformer_mock = Mock()
    transformer_mock.side_effect = lambda raw: TargetModel(raw.symbol)

    svc = ReadOnlyConfigService[str, RawModel, TargetModel](
        adapter=adapter_mock, transformer=transformer_mock, cache=cache_mock
    )

    # 1) Model retrieved from persistance
    out1 = svc.get("AAPL")
    assert out1 == TargetModel("AAPL")

    # assert orchestration
    adapter_mock.get.assert_called_once_with("AAPL")
    transformer_mock.assert_called_once_with(RawModel("AAPL"))
    cache_mock.get.assert_called_once_with("AAPL")
    cache_mock.set.assert_called_once_with("AAPL", TargetModel("AAPL"))

    # 2)  Model retrieved from cache
    cache_mock.reset_mock()
    cache_mock.get.return_value = TargetModel("AAPL") #Similulate real cache

    out2 = svc.get("AAPL")
    assert out2 == TargetModel("AAPL")

    # adapter/transformer not called again as cache hit
    adapter_mock.get.assert_called_once()   # still 1 total
    transformer_mock.assert_called_once()   # still 1 total
    cache_mock.get.assert_called_once_with("AAPL")
    cache_mock.set.assert_not_called()


def test_get_all_transforms_everything_without_using_cache():
    adapter_mock: ConfigPersistenceAdapterProtocol[str, RawModel] = cast(
        ConfigPersistenceAdapterProtocol[str, RawModel],
        Mock(spec=ConfigPersistenceAdapterProtocol)
    )
    cast(Mock, adapter_mock).get_all.return_value = [
        RawModel("AAPL"), RawModel("MSFT")
    ]

    cache_mock = Mock(spec=CacheProtocol)
    transformer_mock = Mock(side_effect=lambda r: TargetModel(r.symbol))

    svc = ReadOnlyConfigService[str, RawModel, TargetModel](
        adapter=adapter_mock, transformer=transformer_mock, cache=cache_mock
    )

    out = svc.get_all()
    assert {t.symbol for t in out} == {"AAPL", "MSFT"}

    # orchestration assertions
    cast(Mock, adapter_mock).get_all.assert_called_once_with()
    # cache is bypassed
    cache_mock.get.assert_not_called()
    cache_mock.set.assert_not_called()
    assert transformer_mock.call_count == 2