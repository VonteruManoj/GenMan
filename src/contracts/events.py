from abc import ABC, abstractmethod


class EventProducerInterface(ABC):
    @abstractmethod
    def close(self):
        """An awaitable produce method."""

    @abstractmethod
    def produce(self, topic, value):
        """Get a JSON from storage"""
