from pathlib import Path
from unittest.mock import MagicMock

import pytest

from core.sessions.container import TradingSessionContainer
from core.sessions.session import TradingSessionService, TradingSessionSettings
from tests.mocks.portfolio import MockPortfolio
from tests.mocks.providers import MockCSVDataProvider, MockIBExecutionProvider


@pytest.fixture
def mock_container():
    container = TradingSessionContainer()

    # Inject mocked settings and services
    container.settings.override(
        TradingSessionSettings(config_dir=Path("/tmp/fake_sessions"))
    )
    container.data_provider_service.override(MockCSVDataProvider())
    container.execution_provider_service.override(MockIBExecutionProvider())
    container.portfolio_service.override(MockPortfolio())

    yield container
    container.unwire()


def test_trading_session_container_resolves_service(mock_container):
    service = mock_container.service()

    assert isinstance(service, TradingSessionService)
    # assert service.sessions_dir == Path("/tmp/fake_sessions")
    assert isinstance(service.data_provider_service, MockCSVDataProvider)
    assert isinstance(service.execution_provider_service, MockIBExecutionProvider)
    assert isinstance(service.portfolio_service, MockPortfolio)