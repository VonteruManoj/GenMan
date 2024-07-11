from abc import ABC, abstractmethod


class AssetsRepositoryInterface(ABC):
    @abstractmethod
    async def get_json_asset(self, key: str) -> dict:
        """Get JSON asset from repository"""
