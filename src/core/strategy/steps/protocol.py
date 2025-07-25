from typing import Any, Protocol, TypeVar

from typing_extensions import deprecated, runtime_checkable


class RuntimeContextProtocol(Protocol):
    def get(self, key: str) -> Any: ...
    def has(self, key: str) -> bool: ...
    def set(self, key: str, value: Any) -> None: ...


class StrategyStepConfigProtocol(Protocol):
    def get(self, key: str) -> Any: ...
    def has(self, key: str) -> bool: ...

T = TypeVar("T")
E = TypeVar("E")


@deprecated("Use Protocols from util.result")
@runtime_checkable
class OkProtocol(Protocol[T]):
    @property
    def value(self) -> T: ...


@deprecated("Use Protocols from util.result")
@runtime_checkable
class ErrProtocol(Protocol[E]):
    @property
    def error(self) -> E: ...


@deprecated("Use Protocols from util.result")
@runtime_checkable
class ResultProtocol(Protocol[T, E]):
    def is_ok(self) -> bool: ...
    def is_err(self) -> bool: ...
    def unwrap(self) -> T: ...
    def unwrap_err(self) -> E: ...