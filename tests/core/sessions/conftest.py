from types import SimpleNamespace

import pytest

from tests.mocks.portfolio import MockPortfolio

from ...mocks.providers import (
    DummyDataProvider,
    MockAlpacaExecutionProvider,
    MockCSVDataProvider,
    MockIBExecutionProvider,
)


@pytest.fixture
def mock_data_provider_service():
    return SimpleNamespace(
        get=lambda key: {
            "csv": MockCSVDataProvider(),
            "dummy": DummyDataProvider(),
        }.get(key)
    )


@pytest.fixture
def mock_execution_provider_service():
    return SimpleNamespace(
        get=lambda key: {
            "ib": MockIBExecutionProvider(),
            "alpaca": MockAlpacaExecutionProvider(),
        }.get(key)
    )


@pytest.fixture
def mock_portfolio_service():
    return SimpleNamespace(
        get=lambda key: MockPortfolio(key) if key == "main_account" else None
    )