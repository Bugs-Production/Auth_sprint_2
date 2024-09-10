from abc import ABC, abstractmethod
from typing import Any


class AbstractCache(ABC):
    """Абстрактный класс для кэширования"""

    def __init__(self, cache_client):
        self.cache_client = cache_client

    @abstractmethod
    async def get_from_cache(self, key: str) -> Any | None:
        pass

    @abstractmethod
    async def put_to_cache(self, key: str, value: Any, ttl: int) -> None:
        pass
