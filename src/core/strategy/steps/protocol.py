from typing import Any, Protocol, TypeVar
from typing_extensions import runtime_checkable


class RuntimeContextProtocol(Protocol):
    def get(self, key: str) -> Any: ...
    def has(self, key: str) -> bool: ...
    def set(self, key: str, value: Any) -> None: ...


class StrategyStepConfigProtocol(Protocol):
    def get(self, key: str) -> Any: ...
    def has(self, key: str) -> bool: ...






T = TypeVar("T")
E = TypeVar("E")

# protocol for result types from result package
@runtime_checkable
class ResultProtocol(Protocol[T, E]):
    ...

# protocol for ok result types
@runtime_checkable
class OkProtocol(Protocol[T]):
    value: T

# protocol for err result types
@runtime_checkable
class ErrProtocol(Protocol[E]):
    error: E
