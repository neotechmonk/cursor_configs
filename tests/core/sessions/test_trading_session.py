from decimal import Decimal

import pytest
from pydantic import ValidationError

from core.sessions.session import (
    RawSessionConfig,
    TradingSessionConfig,
    parse_raw_session_config,
    resolve_session_config,
)
from tests.mocks.portfolio import MockPortfolio


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


# ============================================================================
# SESSION CONFIG MODEL TESTS
# ============================================================================

def test_raw_session_config_model():
    """Test RawSessionConfig creation with valid data."""
    test_data = {
        "name": "Test Session",
        "description": "Unit test session config",
        "portfolio": "test_portfolio",
        "capital_allocation": Decimal("10000.00"),
        "symbols": {
            "BTCUSD": {
                "providers": {"data": "dummy", "execution": "mock_exec"},
                "timeframe": "1m",
                "enabled": True,
                "strategy": "breakout"
            },
            "AAPL": {
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "5m",
                "enabled": False,
                "strategy": "trend-following"
            }
        }
    }
    model = RawSessionConfig(**test_data)

    assert model.name == "Test Session"
    assert model.description == "Unit test session config"
    assert model.portfolio == "test_portfolio"
    assert model.capital_allocation == Decimal("10000.00")
    assert isinstance(model.symbols, dict)
    assert "BTCUSD" in model.symbols
    assert "AAPL" in model.symbols


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

def test_parse_raw_session_config_happy_path():
    """Test parsing raw session configuration from dictionary."""
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
                "enabled": True,
                "strategy": "breakout"
            },
            "AAPL": {
                "providers": {
                    "data": "dummy",
                    "execution": "alpaca"
                },
                "timeframe": "1d",
                "enabled": False,
                "strategy": "trend-following"
            }
        }
    }

    parsed = parse_raw_session_config(raw_dict)

    assert isinstance(parsed, RawSessionConfig)
    assert parsed.name == "Day Trading Session"
    assert parsed.portfolio == "main_account"
    assert parsed.capital_allocation == Decimal("30000.00")
    assert len(parsed.symbols) == 2


def test_parse_raw_session_config_empty_symbols():
    """Test parsing session config with no symbols."""
    raw_dict = {
        "name": "Empty Session",
        "description": "Session with no symbols",
        "portfolio": "main_account",
        "capital_allocation": 10000.00,
        "symbols": {}
    }

    parsed = parse_raw_session_config(raw_dict)
    assert parsed.name == "Empty Session"
    assert len(parsed.symbols) == 0


def test_parse_raw_session_config_missing_required_fields():
    """Test parsing session config with missing required fields."""
    # Missing name
    with pytest.raises(ValidationError, match=r"Field required"):
        parse_raw_session_config({
            "description": "Test session",
            "portfolio": "main_account",
            "capital_allocation": 10000.00,
            "symbols": {}
        })

    # Missing portfolio
    with pytest.raises(ValidationError, match=r"Field required"):
        parse_raw_session_config({
            "name": "Test Session",
            "description": "Test session",
            "capital_allocation": 10000.00,
            "symbols": {}
        })


# ============================================================================
# SESSION RESOLUTION TESTS
# ============================================================================

def test_resolve_session_config_happy_path(
    full_session_config_dict,
    mock_data_provider_service,
    mock_execution_provider_service,
    mock_portfolio_service
):
    """Test successful session configuration resolution."""
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
    assert len(resolved.symbols) == 2


def test_resolve_session_config_missing_portfolio(
    full_session_config_dict,
    mock_data_provider_service,
    mock_execution_provider_service
):
    """Test session resolution with missing portfolio."""
    raw_session = RawSessionConfig(**full_session_config_dict)
    raw_session = raw_session.model_copy(update={"portfolio": "missing_portfolio"})

    # Inject symbol names
    updated_symbols = {
        symbol_name: cfg.model_copy(update={"symbol": symbol_name})
        for symbol_name, cfg in raw_session.symbols.items()
    }
    raw_session = raw_session.model_copy(update={"symbols": updated_symbols})

    # Create a portfolio service that returns None for missing portfolio
    def missing_portfolio_service(name):
        return None

    with pytest.raises(ValueError, match="Error resolving session config"):
        resolve_session_config(
            raw_session,
            data_provider_service=mock_data_provider_service,
            execution_provider_service=mock_execution_provider_service,
            portfolio_service=missing_portfolio_service
        )


# ============================================================================
# SESSION ORCHESTRATION TESTS
# ============================================================================

def test_session_symbol_count():
    """Test that session correctly counts enabled symbols."""
    test_data = {
        "name": "Test Session",
        "portfolio": "test_portfolio",
        "capital_allocation": Decimal("10000.00"),
        "symbols": {
            "AAPL": {
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "5m",
                "enabled": True,
                "strategy": "breakout"
            },
            "SPY": {
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "1d",
                "enabled": False,  # Disabled symbol
                "strategy": "trend-following"
            },
            "BTC": {
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "1h",
                "enabled": True,
                "strategy": "breakout"
            }
        }
    }
    
    model = RawSessionConfig(**test_data)
    enabled_symbols = [symbol for symbol, config in model.symbols.items() if config.enabled]
    
    assert len(enabled_symbols) == 2  # AAPL and BTC are enabled, SPY is disabled


def test_session_capital_allocation():
    """Test session capital allocation validation."""
    # Valid capital allocation
    test_data = {
        "name": "Test Session",
        "portfolio": "test_portfolio",
        "capital_allocation": Decimal("10000.00"),
        "symbols": {}
    }
    
    model = RawSessionConfig(**test_data)
    assert model.capital_allocation == Decimal("10000.00")

    # Zero capital allocation
    test_data["capital_allocation"] = Decimal("0.00")
    model = RawSessionConfig(**test_data)
    assert model.capital_allocation == Decimal("0.00")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_session_end_to_end_workflow(
    mock_data_provider_service,
    mock_execution_provider_service,
    mock_portfolio_service
):
    """Test complete end-to-end session workflow."""
    # 1. Create raw session config
    raw_dict = {
        "name": "Test Session",
        "description": "Test session for workflow",
        "portfolio": "main_account",
        "capital_allocation": 50000.00,
        "symbols": {
            "AAPL": {
                "providers": {"data": "csv", "execution": "ib"},
                "timeframe": "5m",
                "enabled": True,
                "strategy": "breakout"
            }
        }
    }
    
    # 2. Parse raw config
    raw_session = parse_raw_session_config(raw_dict)
    assert raw_session.name == "Test Session"
    assert raw_session.capital_allocation == Decimal("50000.00")
    
    # 3. Inject symbol names
    updated_symbols = {
        symbol_name: cfg.model_copy(update={"symbol": symbol_name})
        for symbol_name, cfg in raw_session.symbols.items()
    }
    raw_session = raw_session.model_copy(update={"symbols": updated_symbols})
    
    # 4. Resolve session
    resolved = resolve_session_config(
        raw_session,
        mock_data_provider_service,
        mock_execution_provider_service,
        mock_portfolio_service
    )
    
    # 5. Validate resolved session
    assert isinstance(resolved, TradingSessionConfig)
    assert resolved.name == "Test Session"
    assert resolved.capital_allocation == 50000.00
    assert len(resolved.symbols) == 1
    assert "AAPL" in resolved.symbols