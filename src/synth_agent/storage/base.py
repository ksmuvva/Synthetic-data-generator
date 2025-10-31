"""Base cloud storage interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class BaseCloudStorage(ABC):
    """Abstract base class for cloud storage providers."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize cloud storage provider.

        Args:
            config: Provider-specific configuration
        """
        self.config = config

    @abstractmethod
    def upload_file(self, local_path: Path, remote_path: str, metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Upload file to cloud storage.

        Args:
            local_path: Local file path
            remote_path: Remote file path/key
            metadata: Optional metadata to attach to the file

        Returns:
            URL or URI of uploaded file
        """
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: Path) -> None:
        """
        Download file from cloud storage.

        Args:
            remote_path: Remote file path/key
            local_path: Local file path to save to
        """
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> None:
        """
        Delete file from cloud storage.

        Args:
            remote_path: Remote file path/key
        """
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> list:
        """
        List files in cloud storage.

        Args:
            prefix: Prefix to filter files

        Returns:
            List of file paths/keys
        """
        pass

    @abstractmethod
    def file_exists(self, remote_path: str) -> bool:
        """
        Check if file exists in cloud storage.

        Args:
            remote_path: Remote file path/key

        Returns:
            True if file exists
        """
        pass

    @abstractmethod
    def get_public_url(self, remote_path: str, expiration_seconds: int = 3600) -> str:
        """
        Get public/signed URL for file.

        Args:
            remote_path: Remote file path/key
            expiration_seconds: URL expiration time in seconds

        Returns:
            Public or signed URL
        """
        pass
