# from types import SimpleNamespace

# import pytest

# from ...mocks.portfolio import MockPortfolio
# from ...mocks.providers import (
#     DummyDataProvider,
#     MockAlpacaExecutionProvider,
#     MockCSVDataProvider,
#     MockIBExecutionProvider,
# )
# from ...mocks.strategies import MockBreakoutStrategy, MockTrendFollowingStrategy


# @pytest.fixture
# def mock_data_provider_service():
#     return SimpleNamespace(
#         get=lambda key: {
#             "csv": MockCSVDataProvider(),
#             "dummy": DummyDataProvider(),
#         }.get(key)
#     )


# @pytest.fixture
# def mock_strategy_service():
#     return SimpleNamespace(
#         get=lambda key: {
#             "breakout": MockBreakoutStrategy(),
#             "trend-following": MockTrendFollowingStrategy(),
#         }.get(key)
#     )


# @pytest.fixture
# def mock_execution_provider_service():
#     return SimpleNamespace(
#         get=lambda key: {
#             "ib": MockIBExecutionProvider(),
#             "alpaca": MockAlpacaExecutionProvider(),
#         }.get(key)
#     )


# @pytest.fixture
# def mock_portfolio_service():
#     return SimpleNamespace(
#         get=lambda key: MockPortfolio(key) if key == "main_account" else None
#     )