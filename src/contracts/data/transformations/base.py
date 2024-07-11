from abc import ABC, abstractmethod
from typing import List


class BaseTransformationInterface(ABC):
    @abstractmethod
    def handle(self) -> List[dict]:
        """Handle transformation"""
