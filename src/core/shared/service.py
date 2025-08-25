from typing import List, Protocol


class ReadOnlyServiceProtocol[Key, T](Protocol):
    def get(self, key: Key) -> T: ...
    def get_all(self) -> List[T]: ...


class PersistenceServiceProtocol[T](Protocol):
    def save(self, obj: T) -> None: ...
    def delete(self, obj: T) -> None: ...


    