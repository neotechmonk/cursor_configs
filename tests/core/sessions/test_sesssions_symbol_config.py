

import pytest

from core.sessions.symbol import (
    RawSymbolConfig,
    SymbolConfigModel,
    parse_raw_symbol_configs,
    resolve_symbol_config_from_raw_model,
)
from core.time import CustomTimeframe
from tests.mocks.providers import (
    DummyDataProvider,
    MockAlpacaExecutionProvider,
    MockCSVDataProvider,
    MockIBExecutionProvider,
)

# --- Mock Provider Classes as given ---
# import from tests/mocks/providers.py
    
# --- Fixtures for mock services ---
# auto imported from module level conftest.py in .sessions


@pytest.fixture
def symbol_config_data():
    return {
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


# --- Integration test ---
def test_full_symbol_config_resolution(
    symbol_config_data,
    mock_data_provider_service,
    mock_execution_provider_service
):
    raw_dict = symbol_config_data["symbols"]

    resolved_models = []

    for symbol_name, raw_cfg in raw_dict.items():
        raw_model = RawSymbolConfig(**raw_cfg)
        resolved_model = resolve_symbol_config_from_raw_model(
            raw_model,
            mock_data_provider_service,
            mock_execution_provider_service
        )
        resolved_models.append(resolved_model)

    assert len(resolved_models) == 2

    cl = next(m for m in resolved_models if m.symbol == "CL")
    aapl = next(m for m in resolved_models if m.symbol == "AAPL")

    assert isinstance(cl.data_provider, MockCSVDataProvider)
    assert isinstance(cl.execution_provider, MockIBExecutionProvider)
    assert str(cl.timeframe) == "5m"  # Use str() instead of .interval

    assert isinstance(aapl.data_provider, DummyDataProvider)
    assert isinstance(aapl.execution_provider, MockAlpacaExecutionProvider)
    assert str(aapl.timeframe) == "1d"  # Use str() instead of .interval