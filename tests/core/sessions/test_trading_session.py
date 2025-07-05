
import pytest

from core.sessions.session import (
    RawSessionConfig,
    TradingSessionConfig,
    resolve_session_config,
)
from core.sessions.symbol import SymbolConfigModel
from tests.mocks.portfolio import MockPortfolio
from tests.mocks.providers import (
    DummyDataProvider,
    MockAlpacaExecutionProvider,
    MockCSVDataProvider,
    MockIBExecutionProvider,
)


@pytest.fixture
def full_session_config_dict():
    return {
        "name": "Day Trading Session",
        "description": "High-frequency trading session for intraday strategies",
        "portfolio": "main_account",
        "capital_allocation": 30000.00,
        "symbols": {
            "CL": {
                "symbol": "CL",
                "providers": {
                    "data": "csv",
                    "execution": "ib"
                },
                "timeframe": "5m",
                "enabled": True,
            },
            "AAPL": {
                "symbol": "AAPL",
                "providers": {
                    "data": "dummy",
                    "execution": "alpaca"
                },
                "timeframe": "1d",
                "enabled": True
            }
        }
    }


def test_resolve_session_config(
    full_session_config_dict,
    mock_data_provider_service,
    mock_execution_provider_service,
    mock_portfolio_service
):
    raw_session = RawSessionConfig(**full_session_config_dict)

    # Inject symbol names into each RawSymbolConfig
    updated_symbols = {
        symbol_name: cfg.model_copy(update={"symbol": symbol_name})
        for symbol_name, cfg in raw_session.symbols.items()
    }
    raw_session = raw_session.model_copy(update={"symbols": updated_symbols})

    resolved = resolve_session_config(
        raw_session,
        data_provider_service=mock_data_provider_service,
        execution_provider_service=mock_execution_provider_service,
        portfolio_service=mock_portfolio_service
    )

    assert isinstance(resolved, TradingSessionConfig)
    assert resolved.name == "Day Trading Session"
    assert resolved.description == "High-frequency trading session for intraday strategies"
    assert isinstance(resolved.portfolio, MockPortfolio)
    assert resolved.capital_allocation == 30000.00
    assert isinstance(resolved.symbols["CL"], SymbolConfigModel)
    assert isinstance(resolved.symbols["AAPL"], SymbolConfigModel)

    cl = resolved.symbols["CL"]
    assert cl.symbol == "CL"
    assert isinstance(cl.data_provider, MockCSVDataProvider)
    assert isinstance(cl.execution_provider, MockIBExecutionProvider)
    assert str(cl.timeframe) == "5m"
    assert cl.enabled is True

    aapl = resolved.symbols["AAPL"]
    assert aapl.symbol == "AAPL"
    assert isinstance(aapl.data_provider, DummyDataProvider)
    assert isinstance(aapl.execution_provider, MockAlpacaExecutionProvider)
    assert str(aapl.timeframe) == "1d"
    assert aapl.enabled is True