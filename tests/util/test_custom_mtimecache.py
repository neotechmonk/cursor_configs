import pytest
from util.custom_cache import MTimeCache  

@pytest.fixture
def cache():
    return MTimeCache[str]()  # Use str as example type for Generic[T]

def test_add_and_get(cache):
    cache.add("config1", "value1")
    assert cache.get("config1") == "value1"

def test_get_missing_key(cache):
    assert cache.get("nonexistent") is None

def test_remove_existing_key(cache):
    cache.add("temp", "to_remove")
    cache.remove("temp")
    assert cache.get("temp") is None

def test_remove_nonexistent_key(cache):
    # Should not raise
    cache.remove("missing")  # No error expected

def test_clear_cache(cache):
    cache.add("one", "1")
    cache.add("two", "2")
    cache.clear()
    assert cache.get("one") is None
    assert cache.get("two") is None
    assert cache.keys() == []

def test_keys(cache):
    cache.add("k1", "v1")
    cache.add("k2", "v2")
    keys = cache.keys()
    assert set(keys) == {"k1", "k2"}