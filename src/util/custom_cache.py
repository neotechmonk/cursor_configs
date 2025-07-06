from pathlib import Path
from typing import Dict, Generic, Optional, TypeVar

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

T = TypeVar("T")


class CustomCache(Generic[T]):
    def __init__(self):
        self._cache: Dict[str, T] = {}

    def add(self, key: str, value: T):
        self._cache[key] = value

    def get(self, key: str) -> Optional[T]:
        return self._cache.get(key)

    def remove(self, key: str):
        self._cache.pop(key, None)

    def clear(self):
        self._cache.clear()

    def keys(self):
        return list(self._cache.keys())
    

class CacheInvalidationHandler(FileSystemEventHandler):
    def __init__(self, cache: CustomCache):
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
    def start(cls, config_dir: Path, cache: CustomCache) -> Observer:
        handler = CacheInvalidationHandler(cache)
        observer = Observer()
        observer.schedule(handler, str(config_dir), recursive=False)
        observer.daemon = True
        observer.start()
        return observer



