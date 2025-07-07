import pytest

from util.custom_cache import WatchedCache


@pytest.fixture()
def test_namespace():
    return "test_namespace"


@pytest.fixture
def cache(test_namespace):
    # Provide a namespace to isolate this test suite
    return WatchedCache[str]()


def test_add_and_get(cache, test_namespace):
    cache.add(ns="test_namespace", key="config1", value="value1")
    assert cache.get(ns=test_namespace, key="config1") == "value1"


def test_get_missing_key(cache, test_namespace):
    assert cache.get(ns=test_namespace, key="nonexistent") is None


def test_remove_existing_key(cache, test_namespace):
    cache.add(ns=test_namespace, key="temp", value="to_remove")
    cache.remove(ns=test_namespace, key="temp")
    assert cache.get(ns=test_namespace, key="temp") is None


def test_remove_nonexistent_key(cache, test_namespace):
    # Should not raise
    cache.remove(ns=test_namespace, key="missing")  # No error expected


def test_clear_cache(cache, test_namespace):
    cache.add(ns=test_namespace, key="one", value="1")
    cache.add(ns=test_namespace, key="two", value="2")
    cache.clear(ns=test_namespace)
    assert cache.get(ns=test_namespace, key="one") is None
    assert cache.get(ns=test_namespace, key="two") is None
    assert cache.keys(ns=test_namespace) == []


def test_keys(cache, test_namespace ):
    cache.add(ns=test_namespace, key="k1", value="v1")
    cache.add(ns=test_namespace, key="k2", value="v2")
    keys = cache.keys(ns=test_namespace)
    assert set(keys) == {"k1", "k2"}


def test_cache_isolation_between_namespaces():
    cache = WatchedCache[str]()
    
    # Add to namespace A
    cache.add(ns="namespace_a", key="shared_key", value="value_a")
    
    # Add to namespace B
    cache.add(ns="namespace_b", key="shared_key", value="value_b")
    
    # Assert: same key, different namespaces → different values
    assert cache.get(ns="namespace_a", key="shared_key") == "value_a"
    assert cache.get(ns="namespace_b", key="shared_key") == "value_b"
    
    # Ensure keys are scoped properly
    assert cache.keys(ns="namespace_a") == ["shared_key"]
    assert cache.keys(ns="namespace_b") == ["shared_key"]

    # Remove from one namespace should not affect the other
    cache.remove(ns="namespace_a", key="shared_key")
    assert cache.get(ns="namespace_a", key="shared_key") is None
    assert cache.get(ns="namespace_b", key="shared_key") == "value_b"

    # Clearing one namespace should not affect the other
    cache.clear(ns="namespace_b")
    assert cache.get(ns="namespace_b", key="shared_key") is None