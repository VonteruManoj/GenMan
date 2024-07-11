from abc import abstractmethod
from typing import Dict, List

from src.contracts.data.transformations.base import BaseTransformationInterface


class SilverToGoldTransformationInterface(BaseTransformationInterface):
    @abstractmethod
    def handle(self) -> List[dict]:
        """Handle transformation"""

    @abstractmethod
    def concat_text(self, content: Dict[str, str]) -> str:
        """Concatenate text"""

    @abstractmethod
    def chunk_text(self, snippets: List[str]) -> List[str]:
        """Chunk text"""

    @abstractmethod
    def embed(self, text: List[str]) -> List[List[float]]:
        """Embed text"""
