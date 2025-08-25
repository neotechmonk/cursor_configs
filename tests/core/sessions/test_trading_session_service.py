from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from core.sessions.session import TradingSession, TradingSessionService
from core.time import CustomTimeframe
from tests.mocks.portfolio import MockPortfolio
from tests.mocks.providers import MockCSVDataProvider, MockIBExecutionProvider


@pytest.fixture
def mock_services():
    return {
        "data_provider_service": MagicMock(get=MagicMock(return_value=MockCSVDataProvider())),
        "execution_provider_service": MagicMock(get=MagicMock(return_value=MockIBExecutionProvider())),
        "portfolio_service": MagicMock(get=MagicMock(return_value=MockPortfolio())),
        "strategy_service": MagicMock(get=MagicMock(return_value=MagicMock()))
    }


@pytest.fixture
def session_yaml_path(tmp_path: Path) -> Path:
    session_data = {
        "name": "Test Session",
        "description": "A test trading session",
        "portfolio": "main_account",
        "capital_allocation": 10000.0,
        "symbols": {
            "AAPL": {
                "strategy": "sample_strategy",
                "providers": {
                    "data": "csv",
                    "execution": "ib"
                },
                "timeframe": "5m",
                "enabled": True
            }
        }
    }

    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    config_file = sessions_dir / "test_session.yaml"
    with open(config_file, "w") as f:
        yaml.safe_dump(session_data, f)

    return sessions_dir


def test_trading_session_service_happy_path(mock_services, session_yaml_path):
    service = TradingSessionService(
        sessions_dir=session_yaml_path,
        data_provider_service=mock_services["data_provider_service"],
        execution_provider_service=mock_services["execution_provider_service"],
        portfolio_service=mock_services["portfolio_service"],
        strategy_service=mock_services["strategy_service"],
    )

    session = service.get("test_session")

    # Verify session object and its core attributes
    assert isinstance(session, TradingSession)
    assert session.name == "Test Session"
    assert session.portfolio.name == "main_account"
    assert session.capital_allocation == 10000.0
    # assert "AAPL" in session.get_enabled_symbols()

    # Verify the resolved symbol config via session accessor
    symbol_cfg = session.get_symbol_config("AAPL")

    assert isinstance(symbol_cfg.data_provider, MockCSVDataProvider)
    assert isinstance(symbol_cfg.execution_provider, MockIBExecutionProvider)
    assert symbol_cfg.timeframe == CustomTimeframe("5m")