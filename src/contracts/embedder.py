from abc import ABC, abstractmethod
from typing import List


class EmbedderInterface(ABC):
    @abstractmethod
    def embed(self, text: str | List[str]) -> List[List[float]]:
        """Embed text"""

    @abstractmethod
    def connect(self):
        """Connect to endpoint"""

    @property
    @abstractmethod
    def connected(self) -> bool:
        """Return connection status"""
