from abc import ABC, abstractmethod


class SlackServiceInterface(ABC):
    @abstractmethod
    def send_message(self, text: str) -> None:
        """Send message to Slack"""

    @abstractmethod
    def send_function_log_message(
        self, name: str, input: str, output: str
    ) -> None:
        """Send function log message to Slack"""
