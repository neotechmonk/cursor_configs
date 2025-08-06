from typing import Protocol, runtime_checkable


@runtime_checkable
class StrategyProtocol(Protocol):
    """Protocol for price feed providers."""


class StrategyServiceProtocol(Protocol):
    def get(self, name: str) -> StrategyProtocol:...
    def get_all(self) -> list[StrategyProtocol]:...