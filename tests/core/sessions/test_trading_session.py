
from decimal import Decimal

import pytest

from core.portfolio.protocol import PortfolioProtocol
from core.sessions.session import (
    RawSessionConfig,
    TradingSessionConfig,
    parse_raw_session_config,
    resolve_session_config,
)
from core.sessions.symbol import RawSymbolConfig, SymbolConfigModel
from core.time import CustomTimeframe
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


def test_raw_session_config_model():
    test_data = {
        "name": "Test Session",
        "description": "Unit test session config",
        "portfolio": "test_portfolio",
        "capital_allocation": Decimal("10000.00"),
        "symbols": {
            "BTCUSD": RawSymbolConfig(
                providers={"data": "dummy", "execution": "mock_exec"},
                timeframe="1m",
                enabled=True,
                symbol="BTCUSD"
            ),
            "AAPL": RawSymbolConfig(
                providers={"data": "csv", "execution": "ib"},
                timeframe="5m",
                enabled=False,
                symbol="AAPL"
            )
        }
    }
    model = RawSessionConfig(**test_data)

    assert model.name == "Test Session"
    assert model.description == "Unit test session config"
    assert model.portfolio == "test_portfolio"
    assert model.capital_allocation == Decimal("10000.00")
    assert isinstance(model.symbols, dict)
    assert "BTCUSD" in model.symbols
    assert model.symbols["BTCUSD"].symbol == "BTCUSD"
    assert model.symbols["AAPL"].enabled is False


def test_trading_session_config_happy_path():

    sample_trading_session_config  =  {
        "name": "Day Trading Session",
        "description": "High-frequency trading session for intraday strategies",
        "portfolio": MockPortfolio(),
        "capital_allocation": 30000.00,
        "symbols": {
            "CL": SymbolConfigModel(
                symbol="CL",
                data_provider=MockCSVDataProvider(),
                execution_provider=MockIBExecutionProvider(),
                timeframe=CustomTimeframe("5m"),
                enabled=True
            ),
            "AAPL": SymbolConfigModel(
                symbol="AAPL",
                data_provider=DummyDataProvider(),
                execution_provider=MockAlpacaExecutionProvider(),
                timeframe=CustomTimeframe("1d"),
                enabled=True
            )
        }
    }
    config = TradingSessionConfig(**sample_trading_session_config)

    assert config.name == "Day Trading Session"
    assert config.description.startswith("High-frequency")
    assert isinstance(config.portfolio, PortfolioProtocol)
    assert config.capital_allocation == 30000.00
    assert "CL" in config.symbols
    assert isinstance(config.symbols["CL"], SymbolConfigModel)
    assert config.symbols["AAPL"].timeframe == CustomTimeframe("1d")


def test_parse_raw_session_config_happy_path():
    # Sample raw input dictionary mimicking YAML structure
    raw_dict = {
        "name": "Day Trading Session",
        "description": "Intraday trading session",
        "portfolio": "main_account",
        "capital_allocation": 30000.00,
        "symbols": {
            "CL": {
                "providers": {
                    "data": "csv",
                    "execution": "ib"
                },
                "timeframe": "5m",
                "enabled": True
            },
            "AAPL": {
                "providers": {
                    "data": "dummy",
                    "execution": "alpaca"
                },
                "timeframe": "1d",
                "enabled": False
            }
        }
    }

    parsed = parse_raw_session_config(raw_dict)

    assert isinstance(parsed, RawSessionConfig)
    assert parsed.name == "Day Trading Session"
    assert parsed.portfolio == "main_account"
    assert parsed.capital_allocation == Decimal("30000.00")

    assert "CL" in parsed.symbols
    assert isinstance(parsed.symbols["CL"], RawSymbolConfig)
    assert parsed.symbols["CL"].symbol == "CL"
    assert parsed.symbols["CL"].providers["data"] == "csv"
    assert parsed.symbols["CL"].enabled is True

    assert parsed.symbols["AAPL"].symbol == "AAPL"
    assert parsed.symbols["AAPL"].enabled is False


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