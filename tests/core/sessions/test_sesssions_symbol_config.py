
from dataclasses import dataclass
from types import SimpleNamespace

import pandas as pd
import pytest

from core.sessions.session import (
    RawSymbolConfig,
    SymbolConfigModel,
    parse_raw_symbol_configs,
    resolve_symbol_config_from_raw_model,
)
from core.time import CustomTimeframe


# --- Mock Provider Classes as given ---
@dataclass
class MockIBExecutionProvider:
    name: str = "ib"
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        print(f"Submitting order for {symbol} on {timeframe} with {order_type} type, quantity {quantity} at {price}")


@dataclass
class MockAlpacaExecutionProvider:
    name: str = "alpaca"
    def submit_order(self, symbol: str, timeframe: str, order_type: str, quantity: int, price: float) -> pd.DataFrame:
        print(f"Submitting order for {symbol} on {timeframe} with {order_type} type, quantity {quantity} at {price}")
    

@dataclass
class MockCSVDataProvider:
    """Mock CSV provider for testing."""
    name: str = "csv"
    
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        print(f"Getting price data for {symbol} on {timeframe}")
        return pd.DataFrame()


@dataclass
class DummyDataProvider:
    """A provider that follows the protocol but doesn't inherit."""
    name: str = "dummy" 
    
    def get_price_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        print(f"Getting price data for {symbol} on {timeframe}")
        return pd.DataFrame()

    
# --- Fixtures for mock services ---
@pytest.fixture
def mock_data_provider_service():
    return SimpleNamespace(get=lambda key: MockCSVDataProvider() if key == "csv" else None)


@pytest.fixture
def mock_execution_provider_service():
    return SimpleNamespace(get=lambda key: MockIBExecutionProvider() if key == "ib" else None)


# @pytest.fixture
# def syombol_config_data():
#     return {
#         "symbols": {
#             "CL": {
#                 "symbol": "CL",
#                     "providers": {
#                         "data": "csv",
#                         "execution": "ib"
#                     },
#                 "timeframe": "5m",
#                     "enabled": True,
#             }, 
#             "AAPL": {
#                 "symbol": "AAPL",
#                     "providers": {
#                         "data": "dummy",
#                         "execution": "alpaca"
#                     },
#                 "timeframe": "1d",
#                     "enabled": True
#                 }
#             }
#     }


# def test_di_coordinating_container_validation():
#     """Test that DI-based coordinating container properly validates providers."""
    
#     # Test with a simple symbol configuration
#     symbol_data = {
#         "symbol": "CL",
#         "providers": {
#             "data": "csv",
#             "execution": "ib"
#         },
#         "timeframe": "5m",
#         "enabled": True
#     }
    
#     config = SymbolConfigModel.model_validate(
#         symbol_data,
#         context={'container': coordinating_container}
#     )
    
#     assert config.symbol == "CL"
#     assert config.timeframe == "5m"
#     assert config.enabled 
#     assert "data" in config.providers
#     assert "execution" in config.providers
#     assert isinstance(config.providers["data"], MockCSVDataProvider)
#     assert isinstance(config.providers["execution"], MockIBExecutionProvider)

# Sample input as if loaded from YAML


def test_raw_symbol_config_happy_path():
    raw_dict = {
    "providers": {
        "data": "csv",
        "execution": "ib"
    },
    "timeframe": "5m",
    "enabled": True
}
    
    # Simulate injecting the key as symbol name
    symbol_key = "AAPL" # real symbol name will be the key in the yaml file
    model = RawSymbolConfig(**raw_dict, symbol=symbol_key)

    assert model.symbol == "AAPL"
    assert model.providers["data"] == "csv"
    assert model.providers["execution"] == "ib"
    assert model.timeframe == "5m"
    assert model.enabled is True


def test_parse_raw_symbol_configs_happy_path():
    sample_raw_yaml_dict = {
        "AAPL": {
            "providers": {"data": "csv", "execution": "ib"},
            "timeframe": "1d",
            "enabled": True
        },
        "BTCUSD": {
            "providers": {"data": "websocket", "execution": "mock"},
            "timeframe": "1m"
        }
    }
    models = parse_raw_symbol_configs(sample_raw_yaml_dict)

    assert len(models) == 2

    model_aapl = next(m for m in models if m.symbol == "AAPL")
    assert model_aapl.providers["data"] == "csv"
    assert model_aapl.timeframe == "1d"
    assert model_aapl.enabled is True

    model_btc = next(m for m in models if m.symbol == "BTCUSD")
    assert model_btc.providers["execution"] == "mock"
    assert model_btc.timeframe == "1m"
    assert model_btc.enabled is True  # default


def test_resolve_symbol_config_from_raw_model_happy_path(
    mock_data_provider_service,
    mock_execution_provider_service
):
    raw = RawSymbolConfig(
        symbol="AAPL",
        providers={"data": "csv", "execution": "ib"},
        timeframe="5m",
        enabled=True
    )

    resolved = resolve_symbol_config_from_raw_model(
        raw,
        data_provider_service=mock_data_provider_service,
        execution_provider_service=mock_execution_provider_service
    )

    assert isinstance(resolved, SymbolConfigModel)
    assert resolved.symbol == "AAPL"
    assert isinstance(resolved.data_provider, MockCSVDataProvider)
    assert isinstance(resolved.execution_provider, MockIBExecutionProvider)
    assert str(resolved.timeframe) == "5m"
    assert resolved.enabled is True


def test_symbol_config_model_validation():
    """Test SymbolConfigModel validation with valid data."""
    
    # Valid symbol configuration as dict
    symbol_data = {
        "symbol": "CL",
        "data-provider": MockCSVDataProvider(),
        "execution-provider": MockIBExecutionProvider(),
        "timeframe": CustomTimeframe("5m") ,
        "enabled": True
    }
    
    # Create the model directly from dict (Pydantic v2 syntax)
    config = SymbolConfigModel(**symbol_data)
    
    assert config.symbol == "CL"
    assert config.timeframe ==CustomTimeframe("5m")
    assert config.enabled is True
    assert config.data_provider.name == "csv"
    assert config.execution_provider.name == "ib"


# def test_symbol_config_model_validation_missing_required_fields():
#     """Test SymbolConfigModel validation with missing required fields."""
    
#     # Missing required fields
#     invalid_data = {
#         "symbol": "CL",
#         # Missing providers, timeframe, enabled
#     }
    
#     with pytest.raises(ValidationError):
#         SymbolConfigModel.model_validate(invalid_data)


# def test_symbol_config_model_validation_invalid_timeframe():
#     """Test SymbolConfigModel validation with invalid timeframe."""
    
#     # Invalid timeframe
#     invalid_data = {
#         "symbol": "CL",
#         "providers": {
#             "data": "csv",
#             "execution": "ib"
#         },
#         "timeframe": "invalid_timeframe",
#         "enabled": True
#     }
    
#     # This will either pass (if no validation) or raise ValidationError
#     try:
#         config = SymbolConfigModel.model_validate(invalid_data)
#         # If it passes, check the timeframe
#         assert config.timeframe == "invalid_timeframe"
#     except ValidationError:
#         # Expected if timeframe validation is implemented
#         pass


# def test_symbol_config_model_validation_defaults():
#     """Test SymbolConfigModel validation with default values."""
    
#     # Minimal valid data (assuming some fields have defaults)
#     minimal_data = {
#         "symbol": "AAPL",
#         "providers": {
#             "data": "yahoo",
#             "execution": "alpaca"
#         },
#         "timeframe": "1d"
#         # enabled should default to True if it has a default
#     }
    
#     config = SymbolConfigModel.model_validate(minimal_data)
    
#     assert config.symbol == "AAPL"
#     assert config.providers["data"] == "yahoo"
#     assert config.providers["execution"] == "alpaca"
