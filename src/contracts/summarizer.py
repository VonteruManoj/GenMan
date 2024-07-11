from abc import ABC, abstractmethod
from typing import List


class SummarizerInterface(ABC):
    @abstractmethod
    def summarize(self, context: str | List[str], question) -> str:
        """Summarize text"""

    @abstractmethod
    def connect(self):
        """Connect to endpoint"""

    @property
    @abstractmethod
    def connected(self) -> bool:
        """Return connection status"""
