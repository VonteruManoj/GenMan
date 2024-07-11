from abc import ABC, abstractmethod


class AIApiClientInterface(ABC):
    @abstractmethod
    def completion(
        prompt: str,
        original_text: str,
        operation: str,
        configs: dict = {},
    ) -> str:
        """Call completion API"""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict],
        original_text: str,
        operation: str,
        configs: dict = {},
    ) -> str:
        """Call chat completion API"""

    @abstractmethod
    def moderation(self, input: str) -> bool:
        """Call moderation API"""

    @abstractmethod
    def set_chain_id(self, chain_id) -> None:
        """Handle the input"""
