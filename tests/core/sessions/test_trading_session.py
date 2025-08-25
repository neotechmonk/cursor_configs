from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from core.sessions.session import (
    RawSessionConfig,
    TradingSession,
    resolve_session_config,
)
from tests.mocks.portfolio import MockPortfolio
from tests.mocks.providers import MockCSVDataProvider, MockIBExecutionProvider
from tests.mocks.strategies import MockBreakoutStrategy, MockStrategyService
from tests.mocks.symbol import MockSymbolConfig


@pytest.fixture
def full_session_config_dict():
    """Sample session configuration data for testing."""
    return {
        "name": "Day Trading Session",
        "description": "High-frequency trading session for intraday strategies",
        "portfolio": "main_account",
        "capital_allocation": 30000.00,
        "symbols": {
            "CL": {
                "providers": {
                    "data": "csv",
                    "execution": "ib"
                },
                "timeframe": "5m",
                "enabled": True,
                "strategy": "breakout"
            },
            "AAPL": {
                "providers": {
                    "data": "dummy",
                    "execution": "alpaca"
                },
                "timeframe": "1d",
                "enabled": True,
                "strategy": "trend-following"
            }
        }
    }


@pytest.fixture
def mock_data_provider_service():
    """Mock data provider service for testing."""
    class MockDataProviderService:
        def get(self, key):
            return {
                "csv": MockCSVDataProvider(),
                "dummy": MockCSVDataProvider(),
            }.get(key)
    return MockDataProviderService()


@pytest.fixture
def mock_execution_provider_service():
    """Mock execution provider service for testing."""
    class MockExecutionProviderService:
        def get(self, key):
            return {
                "ib": MockIBExecutionProvider(),
                "alpaca": MockIBExecutionProvider(),
            }.get(key)
    return MockExecutionProviderService()


@pytest.fixture
def mock_portfolio_service():
    """Mock portfolio service for testing."""
    class MockPortfolioService:
        def get(self, name):
            return MockPortfolio(name) if name == "main_account" else None
    return MockPortfolioService()


@pytest.fixture
def mock_strategy_service():
    """Mock strategy service for testing."""
    return MockStrategyService()


# ============================================================================
# SESSION CONFIG MODEL TESTS
# ============================================================================

def test_raw_session_config_model():
    """Test RawSessionConfig model creation with new list-based symbols structure.
    
    Verifies that the model correctly handles the new YAML format where
    symbols are defined as a list with explicit symbol fields instead of
    being keyed by symbol names.
    """
    test_data = {
        "name": "Test Session",
        "description": "Unit test session config",
        "portfolio": "test_portfolio",
        "capital_allocation": Decimal("10000.00"),
        "symbols": [
            {
                "symbol": "BTCUSD",
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "5m",
                "enabled": True,
                "strategy": "breakout",
            },
            {
                "symbol": "ETHUSD",
                "providers": {"data": "yahoo", "execution": "ib"},
                "timeframe": "1h",
                "enabled": False,
                "strategy": "trend",
            }
        ]
    }
    
    config = RawSessionConfig(**test_data)
    assert config.name == "Test Session"
    assert config.description == "Unit test session config"
    assert config.portfolio == "test_portfolio"
    assert config.capital_allocation == Decimal("10000.00")
    assert len(config.symbols) == 2
    assert config.symbols[0]["symbol"] == "BTCUSD"
    assert config.symbols[1]["symbol"] == "ETHUSD"


def test_raw_session_config_validation():
    """Test RawSessionConfig validation with invalid data."""
    # Missing required fields
    with pytest.raises(ValidationError, match=r"Field required"):
        RawSessionConfig(
            name="Test Session",
            # missing portfolio
            capital_allocation=Decimal("10000.00"),
            symbols={}
        )

    # Missing symbols field
    with pytest.raises(ValidationError, match=r"Field required"):
        RawSessionConfig(
            name="Test Session",
            portfolio="test_portfolio",
            capital_allocation=Decimal("10000.00")
            # missing symbols
        )


# ============================================================================
# SESSION CONFIG PARSING TESTS
# ============================================================================

def test_raw_session_config_with_symbol_names():
    """Test RawSessionConfig with explicit symbol names in the new list structure.
    
    Verifies that symbol names are properly extracted from the explicit
    'symbol' field in each symbol configuration item.
    """
    test_data = {
        "name": "Test Session",
        "description": "Unit test session config",
        "portfolio": "test_portfolio",
        "capital_allocation": Decimal("10000.00"),
        "symbols": [
            {
                "symbol": "BTCUSD",
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "5m",
                "enabled": True,
                "strategy": "breakout",
            }
        ]
    }
    
    config = RawSessionConfig(**test_data)
    assert config.symbols[0]["symbol"] == "BTCUSD"


def test_raw_session_config_empty_symbols():
    """Test RawSessionConfig with empty symbols list in the new structure.
    
    Verifies that the model correctly handles empty symbol lists
    in the new list-based YAML format.
    """
    test_data = {
        "name": "Test Session",
        "description": "Unit test session config",
        "portfolio": "test_portfolio",
        "capital_allocation": Decimal("10000.00"),
        "symbols": []
    }
    
    config = RawSessionConfig(**test_data)
    assert len(config.symbols) == 0


def test_raw_session_config_missing_required_fields():
    """Test RawSessionConfig validation for missing required fields."""
    # Test missing name
    with pytest.raises(ValidationError):
        RawSessionConfig(
            description="Test session",
            portfolio="test_portfolio",
            capital_allocation=Decimal("10000.00"),
            symbols=[]
        )
    
    # Test missing portfolio
    with pytest.raises(ValidationError):
        RawSessionConfig(
            name="Test Session",
            description="Test session",
            capital_allocation=Decimal("10000.00"),
            symbols=[]
        )
    
    # Test missing capital_allocation
    with pytest.raises(ValidationError):
        RawSessionConfig(
            name="Test Session",
            description="Test session",
            portfolio="test_portfolio",
            symbols=[]
        )


# ============================================================================
# SESSION RESOLUTION TESTS
# ============================================================================

def test_resolve_session_config_happy_path():
    """Test resolve_session_config happy path with new list-based structure.
    
    Verifies that the session configuration resolution works correctly
    with the new list-based symbols format where each symbol has an
    explicit 'symbol' field.
    """
    raw_config = RawSessionConfig(
        name="Test Session",
        description="Test session",
        portfolio="test_portfolio",
        capital_allocation=Decimal("10000.00"),
        symbols=[
            {
                "symbol": "BTCUSD",
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "5m",
                "enabled": True,
                "strategy": "breakout",
            }
        ]
    )
    
    # Mock services
    mock_data_service = MagicMock()
    mock_exec_service = MagicMock()
    mock_portfolio_service = MagicMock()
    mock_strategy_service = MagicMock()
    
    # Mock portfolio service to return a portfolio
    mock_portfolio = MockPortfolio()
    mock_portfolio_service.get.return_value = mock_portfolio
    
    # Mock data and execution providers to return proper types
    mock_data_provider = MockCSVDataProvider()
    mock_exec_provider = MockIBExecutionProvider()
    mock_strategy = MockBreakoutStrategy()
    
    mock_data_service.get.return_value = mock_data_provider
    mock_exec_service.get.return_value = mock_exec_provider
    mock_strategy_service.get.return_value = mock_strategy
    
    # Resolve the config
    resolved_config = resolve_session_config(
        raw_config,
        mock_data_service,
        mock_exec_service,
        mock_portfolio_service,
        mock_strategy_service
    )
    
    # Verify the resolved config
    assert resolved_config.name == "Test Session"
    assert resolved_config.portfolio == mock_portfolio
    assert len(resolved_config.symbols) == 1
    assert resolved_config.symbols[0].symbol == "BTCUSD"


def test_resolve_session_config_missing_portfolio():
    """Test resolve_session_config with missing portfolio in new structure.
    
    Verifies that portfolio validation works correctly with the new
    list-based symbols format and proper error handling.
    """
    raw_config = RawSessionConfig(
        name="Test Session",
        description="Test session",
        portfolio="missing_portfolio",
        capital_allocation=Decimal("10000.00"),
        symbols=[
            {
                "symbol": "BTCUSD",
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "5m",
                "enabled": True,
                "strategy": "breakout",
            }
        ]
    )
    
    # Mock services
    mock_data_service = MagicMock()
    mock_exec_service = MagicMock()
    mock_portfolio_service = MagicMock()
    mock_strategy_service = MagicMock()
    
    # Mock portfolio service to return None (missing portfolio)
    mock_portfolio_service.get.return_value = None
    
    # Mock data and execution providers to return proper types
    mock_data_provider = MockCSVDataProvider()
    mock_exec_provider = MockIBExecutionProvider()
    mock_strategy = MockBreakoutStrategy()
    
    mock_data_service.get.return_value = mock_data_provider
    mock_exec_service.get.return_value = mock_exec_provider
    mock_strategy_service.get.return_value = mock_strategy
    
    # Should raise ValueError for missing portfolio
    with pytest.raises(ValueError, match="portfolio 'missing_portfolio' not found"):
        resolve_session_config(
            raw_config,
            mock_data_service,
            mock_exec_service,
            mock_portfolio_service,
            mock_strategy_service
        )


# ============================================================================
# SESSION ORCHESTRATION TESTS
# ============================================================================

def test_session_symbol_count():
    """Test session symbol count."""
    # Create a session with 2 symbols
    session = TradingSession(
        name="Test Session",
        portfolio=MockPortfolio(),
        capital_allocation=Decimal("10000.00"),
        symbols={
            "BTCUSD": MockSymbolConfig(enabled=True),
            "ETHUSD": MockSymbolConfig(enabled=False)
        }
    )
    
    # Should have 2 total symbols
    assert len(session._symbols) == 2
    
    # Should have 1 enabled symbol
    enabled_symbols = session.get_enabled_symbols()
    assert len(enabled_symbols) == 1
    assert "BTCUSD" in enabled_symbols


def test_session_capital_allocation():
    """Test session capital allocation."""
    session = TradingSession(
        name="Test Session",
        portfolio=MockPortfolio(),
        capital_allocation=Decimal("50000.00"),
        symbols={
            "BTCUSD": MockSymbolConfig(enabled=True)
        }
    )
    
    assert session.capital_allocation == Decimal("50000.00")
    assert session.portfolio == MockPortfolio()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_session_end_to_end_workflow():
    """Test complete session workflow with new list-based structure.
    
    Verifies the entire session workflow from raw YAML configuration
    to fully resolved session object using the new list-based symbols
    format with explicit symbol fields.
    """
    # Create raw config with new list structure
    raw_config = RawSessionConfig(
        name="Test Session",
        description="End-to-end test session",
        portfolio="test_portfolio",
        capital_allocation=Decimal("10000.00"),
        symbols=[
            {
                "symbol": "BTCUSD",
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "5m",
                "enabled": True,
                "strategy": "breakout",
            }
        ]
    )
    
    # Mock services
    mock_data_service = MagicMock()
    mock_exec_service = MagicMock()
    mock_portfolio_service = MagicMock()
    mock_strategy_service = MagicMock()
    
    # Mock portfolio service to return a portfolio
    mock_portfolio = MockPortfolio()
    mock_portfolio_service.get.return_value = mock_portfolio
    
    # Mock data and execution providers to return proper types
    mock_data_provider = MockCSVDataProvider()
    mock_exec_provider = MockIBExecutionProvider()
    mock_strategy = MockBreakoutStrategy()
    
    mock_data_service.get.return_value = mock_data_provider
    mock_exec_service.get.return_value = mock_exec_provider
    mock_strategy_service.get.return_value = mock_strategy
    
    # Resolve the config
    resolved_config = resolve_session_config(
        raw_config,
        mock_data_service,
        mock_exec_service,
        mock_portfolio_service,
        mock_strategy_service
    )
    
    # Verify the resolved config
    assert resolved_config.name == "Test Session"
    assert resolved_config.portfolio == mock_portfolio
    assert len(resolved_config.symbols) == 1
    assert resolved_config.symbols[0].symbol == "BTCUSD"