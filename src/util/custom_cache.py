from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Protocol, TypeVar

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

T = TypeVar("T")


@dataclass
class Cache[T](Protocol):
    # _namespace:str :

    def add(self, key:str, value: T)-> None :...    
    def get(self, key:str) -> T:...
    def get_all(self)-> list[T]:...
    def clear(self)-> None:...


class WatchedCache[T]():
    def __init__(self):
        self._store: Dict[str, Dict[str, T]] = {}

    def _ensure_namespace(self, ns: str):
        if ns not in self._store:
            self._store[ns] = {}

    def add(self, ns: str, key: str, value: T):
        self._ensure_namespace(ns)
        self._store[ns][key] = value

    def get(self, ns: str, key: str) -> Optional[T]:
        return self._store.get(ns, {}).get(key)
    
    def get_all(self, ns: str) -> list[T]:
        return list(self._store.get(ns, {}).values())

    def remove(self, ns: str, key: str):
        self._store.get(ns, {}).pop(key, None)

    def clear(self, ns: str):
        self._store.pop(ns, None)

    def keys(self, ns: str):
        return list(self._store.get(ns, {}).keys())


class ScopedCacheView[T]():
    def __init__(self, cache: WatchedCache[T], namespace: str):
        self._cache = cache
        self._namespace = namespace

    def add(self, key: str, value: T):
        self._cache.add(self._namespace, key, value)

    def get(self, key: str) -> Optional[T]:
        return self._cache.get(self._namespace, key)
    
    def get_all(self) -> list[T]:
        return self._cache.get_all(self._namespace)

    def remove(self, key: str):
        self._cache.remove(self._namespace, key)

    def clear(self):
        self._cache.clear(self._namespace)

    def keys(self):
        return self._cache.keys(self._namespace)    


class CacheInvalidationHandler(FileSystemEventHandler):
    def __init__(self, cache: ScopedCacheView):
        self.cache = cache

    def on_modified(self, event):
        if not event.is_directory:
            name = Path(event.src_path).stem
            # print("on_modified: " + name)
            self.cache.remove(name)

    def on_deleted(self, event):
        if not event.is_directory:
            name = Path(event.src_path).stem
            # print("on_deleted: " + name)
            self.cache.remove(name)

    @classmethod
    def start(cls, config_dir: Path, cache: WatchedCache) -> Observer:
        handler = CacheInvalidationHandler(cache)
        observer = Observer()
        observer.schedule(handler, str(config_dir), recursive=False)
        observer.daemon = True
        observer.start()
        return observer



