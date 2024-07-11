from unittest.mock import patch

from fakeredis import FakeRedis

from src.util.cache import Cache, RedisCache


# ----------------------------------------------
# Cache
# ----------------------------------------------
@patch("src.util.cache.Cache.__abstractmethods__", set())
def test_get_prefixed_key():
    cache = Cache()
    assert cache._formulate_key("key") == "ai-service-test:key"


# ----------------------------------------------
# RedisCache
# ----------------------------------------------
def test_redis_cache_get_missing_key_is_none():
    cache = RedisCache(FakeRedis())

    assert cache.get("key") is None


def test_redis_cache_crud():
    cache = RedisCache(FakeRedis())
    value = "value"

    # Set the key.
    assert cache.set("key", value) is True
    # Get the key.
    assert cache.get("key") == value
    # Check if the key exists.
    assert cache.exists("key") == 1
    # Delete the key.
    delete_result = cache.delete("key")
    assert delete_result == 1
