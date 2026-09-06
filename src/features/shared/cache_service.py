import json
from abc import ABC, abstractmethod


class CacheEntry:
    """Represents the value to be cached along with its optional time-to-live (TTL)."""

    def __init__(self, value, ttl: int | None = None):
        self.value = value
        self.ttl = ttl

    def get_ttl(self) -> int | None:
        """
        Get the time-to-live (TTL) of the cache entry.

        Returns:
            int | None: Value's time-to-live (TTL) in seconds, or None if not set.
        """
        return self.ttl

    def get_json_value(self):
        """
        Get the JSON-decoded value of the cache entry.
        Returns:
            dict | list: The JSON-decoded value of the cache entry.
        """
        return json.loads(self.value)


class CacheService(ABC):
    @abstractmethod
    async def get(self, key: str) -> CacheEntry | None:
        """
        Retrieve a value from the cache by its key.

        :param key: The key of the cached value.
        :return: The cached value, or None if not found.
        """
        pass

    @abstractmethod
    async def set(self, key: str, cache_entry: CacheEntry):
        """
        Set a value in the cache with an optional time-to-live (TTL).

        :param key: The key under which to store the value.
        :param cache_entry: The cache entry to store, including its value and optional TTL.
        """
        pass

    @abstractmethod
    async def delete(self, key: str):
        """
        Delete a value from the cache by its key.

        :param key: The key of the value to delete.
        """
        pass
