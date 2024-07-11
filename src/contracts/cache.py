from abc import ABC, abstractmethod


class CacheInterface(ABC):
    @abstractmethod
    def get(self, key: str) -> any:
        """Get value from cache"""

    @abstractmethod
    def set(self, key: str, value: str, ttl: float | None = None) -> None:
        """Set value to cache"""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache"""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
