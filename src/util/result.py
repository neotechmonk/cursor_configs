from typing import Protocol, runtime_checkable

from result import Err as LibErr
from result import Ok as LibOk
from result import Result as LibResult


@runtime_checkable
class OkProtocol[T](Protocol):
    @property
    def value(self) -> T: ...


@runtime_checkable
class ErrProtocol[E](Protocol):
    @property
    def error(self) -> E: ...


@runtime_checkable
class ResultProtocol[T, E](Protocol):
    def is_ok(self) -> bool: ...
    def is_err(self) -> bool: ...
    def unwrap(self) -> T: ...
    def unwrap_err(self) -> E: ...


class Ok[T]():
    """
    implements OkProtocol[T]
    """
    def __init__(self, value: T):
        self._inner = LibOk(value)

    @property
    def value(self) -> T:
        return self._inner.ok_value

    def to_result(self) -> LibResult:
        return self._inner


class Err[E]():
    """
    implements ErrProtocol[E]
    """
    def __init__(self, error: E):
        self._inner = LibErr(error)

    @property
    def error(self) -> E:
        return self._inner.err_value

    def to_result(self) -> LibResult:
        return self._inner


class Result[T, E]():
    """
    implements ResultProtocol[T, E]
    """
    def __init__(self, result: LibResult):
        self._inner = result

    @classmethod
    def ok(cls, value: T) -> "Result[T, E]":
        return cls(LibOk(value))

    @classmethod
    def err(cls, error: E) -> "Result[T, E]":
        return cls(LibErr(error))

    def is_ok(self) -> bool:
        return self._inner.is_ok()

    def is_err(self) -> bool:
        return self._inner.is_err()

    def unwrap(self) -> T:
        return self._inner.unwrap()

    def unwrap_err(self) -> E:
        return self._inner.unwrap_err()