import json

import redis as redis

from src.contracts.cache import CacheInterface
from src.core.config import get_settings


class Cache(CacheInterface):
    def __init__(self):
        self._key_prefix: str = get_settings().APP_NAME

    def _formulate_key(self, key: str) -> str:
        """Formulate a key with prefix.

        Parameters
        ----------
        key : str
            Key to formulate.

        Returns
        -------
        str
        """

        return f"{self._key_prefix}:{key}"


class RedisCache(Cache):
    def __init__(self, client: redis.Redis):
        super().__init__()
        self._client = client

    @property
    def client(self) -> redis.Redis:
        return self._client

    def get(self, key: str) -> any:
        """Get a value from Redis.

        Parameters
        ----------
        key : str
            Key to get.

        Returns
        -------
        any
        """

        value = self._client.get(name=self._formulate_key(key))

        return None if value is None else json.loads(value)

    def set(
        self, key: str, value: str, ttl: float | None = None
    ) -> bool | None:
        """Set a key-value pair in Redis.

        Parameters
        ----------
        key : str
            Key to set.
        value : str
            Value to set.
        ttl : float | None, optional
            Time to live in seconds, by default None
        """

        return self._client.set(
            self._formulate_key(key),
            json.dumps(value, separators=(",", ":")),
            ttl,
        )

    def delete(self, key: str) -> int:
        """Delete a key from Redis.

        Parameters
        ----------
        key : str
            Key to delete.
        """

        return self.client.delete(self._formulate_key(key))

    def exists(self, key: str) -> int:
        """Check if a key exists in Redis.

        Parameters
        ----------
        key : str
            Key to check.

        Returns
        -------
        int
            Return the number of keys that exist.
        """

        return self.client.exists(self._formulate_key(key))
