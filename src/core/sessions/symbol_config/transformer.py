
from dataclasses import dataclass

from core.data_provider.protocol import DataProviderProtocol
from core.execution_provider.protocol import ExecutionProviderProtocol
from core.sessions.symbol_config.model import RawSymbolConfig, SymbolConfigModel
from core.shared.service import ReadOnlyServiceProtocol
from core.strategy.protocol import StrategyProtocol


@dataclass(slots=True)
class SymbolTransformer:
    """Implements ConfigTransformerProtocol[RawSymbolConfig, SymbolConfigModel]."""
    data_service: ReadOnlyServiceProtocol[str, DataProviderProtocol]
    exec_service: ReadOnlyServiceProtocol[str, ExecutionProviderProtocol]
    strategy_service: ReadOnlyServiceProtocol[str, StrategyProtocol]

    def __call__(self, raw: RawSymbolConfig) -> SymbolConfigModel:
        data_provider = self.data_service.get(raw.providers["data"])
        exec_provider = self.exec_service.get(raw.providers["execution"])
        strategy = self.strategy_service.get(raw.strategy)
        if data_provider is None or exec_provider is None or strategy is None:
            raise ValueError("Symbol resolution failed: one or more dependencies missing")
        return SymbolConfigModel(
            symbol=raw.symbol,
            timeframe=raw.timeframe,
            enabled=raw.enabled,
            data_provider=data_provider,
            execution_provider=exec_provider,
            strategy=strategy,
        )