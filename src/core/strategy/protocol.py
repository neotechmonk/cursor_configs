from typing import Protocol, runtime_checkable


@runtime_checkable
class StrategyProtocol(Protocol):
    """Protocol for price feed providers."""