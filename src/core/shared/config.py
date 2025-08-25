from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, List, Optional, Protocol, TypeVar, runtime_checkable

ConfigKey = TypeVar("ConfigKey")                  # e.g., "AAPL", session name, UUID, etc.
RawConfigModel = TypeVar("RawConfigModel")        # raw form from persistence (YAML/DB/API)
TargetConfigModel = TypeVar("TargetConfigModel")  # fully resolved, domain-ready model


@runtime_checkable
class ConfigPersistenceAdapterProtocol[ConfigKey, RawConfigModel](Protocol):
    """Backend specific - yaml, json, db, api"""
    def get(self, key: ConfigKey) -> RawConfigModel: ...
    def get_all(self) -> list[RawConfigModel]: ...


class ConfigTransformerProtocol[RawConfigModel, TargetConfigModel](Protocol):
    """Transform raw config model to target config model"""
    def __call__(self, raw: RawConfigModel) -> TargetConfigModel: ...


class CacheProtocol[Key, TargetConfigModel](Protocol):
    def get(self, key: Key) -> Optional[TargetConfigModel]: ...
    def set(self, key: Key, value: TargetConfigModel) -> None: ...
    def clear(self) -> None: ...


# Optional: handy no-op transformer for cases where Raw == Resolved
class IdentityTransformer[RawConfigModel]:
    def __call__(self, raw: RawConfigModel) -> RawConfigModel:
        return raw


@dataclass(slots=True)
class ReadOnlyConfigService(Generic[ConfigKey, RawConfigModel, TargetConfigModel]):
    """
    Generic read-only service:
      • fetches Raw via adapter
      • transforms Raw -> Target
      • optionally caches Target (read-through) using the provided key

    Notes:
      - Cache keys are exactly the keys passed to `get(key)`
      - `get_all()` returns transformed items WITHOUT priming the cache
    """
    adapter: ConfigPersistenceAdapterProtocol[ConfigKey, RawConfigModel]
    transformer: Callable[[RawConfigModel], TargetConfigModel]
    cache: Optional[CacheProtocol[ConfigKey, TargetConfigModel]] = None

    def get(self, key: ConfigKey) -> TargetConfigModel:
        if self.cache:
            cached = self.cache.get(key)
            if cached is not None:
                return cached

        raw = self.adapter.get(key)
        target = self.transformer(raw)

        if self.cache:
            self.cache.set(key, target)
        return target

    def get_all(self) -> List[TargetConfigModel]:
        raws = self.adapter.get_all()
        return [self.transformer(r) for r in raws]

