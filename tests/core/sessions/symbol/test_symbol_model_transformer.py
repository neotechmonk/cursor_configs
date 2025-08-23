from core.sessions.symbol_config.model import RawSymbolConfig, SymbolConfigModel
from core.sessions.symbol_config.transformer import SymbolTransformer
from core.shared.config import ConfigTransformerProtocol
from core.time import CustomTimeframe
from tests.mocks.providers import MockDataProviderService, MockExecutionProviderService
from tests.mocks.strategies import MockStrategyService


def test_symbol_transformer_happy_path():
    # Arrange
    raw = RawSymbolConfig(
        symbol="AAPL",
        timeframe="5m",
        enabled=True,
        providers={"data": "csv", "execution": "ib"},
        strategy="breakout",
    )

    transformer: ConfigTransformerProtocol[RawSymbolConfig, SymbolConfigModel] = SymbolTransformer(
        data_service=MockDataProviderService(),
        exec_service=MockExecutionProviderService(),
        strategy_service=MockStrategyService(),
    )

    # Act
    model = transformer(raw)

    # Assert
    assert isinstance(model, SymbolConfigModel)
    assert model.symbol == "AAPL"
    assert model.timeframe == CustomTimeframe("5m")
    assert model.enabled is True
    assert model.data_provider.name == "csv"
    assert model.execution_provider.name == "ib"
    assert model.strategy.name == "breakout"