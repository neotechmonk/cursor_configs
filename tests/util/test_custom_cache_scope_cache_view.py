import pytest

from util.custom_cache import ScopedCacheView, WatchedCache


@pytest.fixture
def base_cache():
    return WatchedCache[str]()


@pytest.fixture
def scoped_view(base_cache):
    return ScopedCacheView[str](cache=base_cache, namespace="scoped_ns")


def test_scoped_add_and_get(scoped_view):
    scoped_view.add("item1", "value1")
    assert scoped_view.get("item1") == "value1"


def test_scoped_get_missing_key(scoped_view):
    assert scoped_view.get("missing") is None


def test_scoped_remove_existing_key(scoped_view):
    scoped_view.add("temp", "value")
    scoped_view.remove("temp")
    assert scoped_view.get("temp") is None


def test_scoped_remove_nonexistent_key(scoped_view):
    # Should not raise
    scoped_view.remove("ghost")


def test_scoped_clear(scoped_view):
    scoped_view.add("one", "1")
    scoped_view.add("two", "2")
    scoped_view.clear()
    assert scoped_view.get("one") is None
    assert scoped_view.get("two") is None
    assert scoped_view.keys() == []


def test_scoped_keys(scoped_view):
    scoped_view.add("k1", "v1")
    scoped_view.add("k2", "v2")
    keys = scoped_view.keys()
    assert set(keys) == {"k1", "k2"}


def test_scope_isolation(base_cache):
    view1 = ScopedCacheView(cache=base_cache, namespace="ns1")
    view2 = ScopedCacheView(cache=base_cache, namespace="ns2")

    view1.add("shared", "v1")
    view2.add("shared", "v2")

    assert view1.get("shared") == "v1"
    assert view2.get("shared") == "v2"

    view1.remove("shared")
    assert view1.get("shared") is None
    assert view2.get("shared") == "v2"