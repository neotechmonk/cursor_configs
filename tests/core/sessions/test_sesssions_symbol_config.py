
import pytest

from core.sessions.symbol_config import (
    RawSymbolConfig,
    resolve_symbol_config_from_raw_model,
)
from tests.mocks.providers import MockDataProviderService, MockExecutionProviderService
from tests.mocks.strategies import MockStrategyService


@pytest.mark.parametrize(
    "providers",
    [
        {},  # empty
        # {"data": "csv"},  # missing execution
        {"execution": "ib"},  # missing data
        {"data": "csv", "execution": "ib", "extra": "invalid"}  # extra key
    ]
)
def test_invalid_provider_keys(providers):
    with pytest.raises(ValueError, match=r"Input should be 'data' or 'execution'|Missing provider/s:"):
        RawSymbolConfig(
            providers=providers,
            timeframe="5m",
            strategy="breakout",
            symbol="AAPL"
        )


@pytest.mark.parametrize(
    "symbol, data_provider, execution_provider, timeframe, strategy",
    [
        ("AAPL", "csv", "ib", "5m", "breakout"),
        ("BTCUSD", "websocket", "mock", "1m", "breakout")
    ]
)
def test_raw_symbol_config_creation(symbol, data_provider, execution_provider, timeframe, strategy):
    model = RawSymbolConfig(
        symbol=symbol,
        providers={"data": data_provider, "execution": execution_provider},
        timeframe=timeframe,
        strategy=strategy,
        enabled=True
    )
    assert model.symbol == symbol
    assert model.providers["data"] == data_provider
    assert model.providers["execution"] == execution_provider
    assert model.timeframe == timeframe
    assert model.strategy == strategy


@pytest.mark.parametrize(
    "providers",
    [
        {"data": "missing", "execution": "ib"},       # bad data provider
        {"data": "csv", "execution": "missing"}       # bad execution provider
    ]
)
def test_resolve_symbol_config_with_missing_providers(providers):
    raw = RawSymbolConfig(
        symbol="AAPL",
        providers=providers,
        timeframe="5m",
        strategy="trend-following",
        enabled=True
    )

    with pytest.raises(ValueError, match="Error resolving symbol config"):
        resolve_symbol_config_from_raw_model(
            raw,
            MockDataProviderService(),
            MockExecutionProviderService(),
            MockStrategyService()
        )