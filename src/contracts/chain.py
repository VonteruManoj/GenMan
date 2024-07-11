from abc import ABC, abstractmethod


class ChainableServicesInterface(ABC):
    """
    Interface for services that can be chained together
    """

    @abstractmethod
    def handle(self, input: str, **kwargs) -> str:
        """Handle the input"""

    @abstractmethod
    def set_chain_id(self, chain_id) -> None:
        """Handle the input"""


class ChainResolverInterface(ABC):
    """
    Interface for a chain resolver
    """

    @abstractmethod
    def __init__(self, services: list[ChainableServicesInterface]) -> None:
        """Initialize chain resolver"""

    @abstractmethod
    def resolve(self, input: str, **kwargs) -> str:
        """Resolve the chain"""
