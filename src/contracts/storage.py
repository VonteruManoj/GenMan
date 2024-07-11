from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    def get_file(self, key: str, bucket: str | None = None) -> any:
        """Get file from storage"""

    @abstractmethod
    def get_json(self, key: str, bucket: str | None = None) -> dict:
        """Get a JSON from storage"""

    @abstractmethod
    def put_file(self, key: str, data: any, bucket: str | None = None) -> None:
        """Set file in storage"""

    @abstractmethod
    def put_json(
        self, key: str, data: dict, bucket: str | None = None
    ) -> None:
        """Set a JSON in storage"""

    @abstractmethod
    def list_files(
        self, bucket: str | None = None, prefix: str = ""
    ) -> list[str]:
        """List files in storage"""

    @abstractmethod
    def delete_file(self, key: str, bucket: str | None = None) -> None:
        """Delete file in storage"""
