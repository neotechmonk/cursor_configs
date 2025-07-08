import pytest
from util.custom_cache import ScopedCacheView, WatchedCache


@pytest.fixture
def scoped_cache_view() -> ScopedCacheView[str]:
    base_cache = WatchedCache[str]()
    return ScopedCacheView(cache=base_cache, namespace="test_ns")


def test_add_and_get(scoped_cache_view):
    scoped_cache_view.add("key1", "val1")
    assert scoped_cache_view.get("key1") == "val1"


def test_get_missing_returns_none(scoped_cache_view):
    assert scoped_cache_view.get("missing_key") is None


def test_remove_existing_key(scoped_cache_view):
    scoped_cache_view.add("temp", "value")
    scoped_cache_view.remove("temp")
    assert scoped_cache_view.get("temp") is None


def test_remove_nonexistent_key_is_safe(scoped_cache_view):
    scoped_cache_view.remove("nonexistent")  # Should not raise


def test_clear_namespace(scoped_cache_view):
    scoped_cache_view.add("a", "1")
    scoped_cache_view.add("b", "2")
    scoped_cache_view.clear()
    assert scoped_cache_view.get("a") is None
    assert scoped_cache_view.get("b") is None


def test_keys(scoped_cache_view):
    scoped_cache_view.add("x", "valX")
    scoped_cache_view.add("y", "valY")
    keys = scoped_cache_view.keys()
    assert set(keys) == {"x", "y"}


def test_get_all(scoped_cache_view):
    scoped_cache_view.add("one", "v1")
    scoped_cache_view.add("two", "v2")
    values = scoped_cache_view.get_all()
    assert set(values) == {"v1", "v2"}


def test_namespace_isolation():
    base = WatchedCache[str]()
    view1 = ScopedCacheView(cache=base, namespace="ns1")
    view2 = ScopedCacheView(cache=base, namespace="ns2")

    view1.add("shared", "v1")
    view2.add("shared", "v2")

    assert view1.get("shared") == "v1"
    assert view2.get("shared") == "v2"

    view1.remove("shared")
    assert view1.get("shared") is None
    assert view2.get("shared") == "v2"