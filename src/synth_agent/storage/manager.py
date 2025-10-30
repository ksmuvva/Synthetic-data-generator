"""Storage manager for cloud storage providers."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from synth_agent.core.config import Config
from synth_agent.core.exceptions import StorageError
from synth_agent.storage.base import BaseCloudStorage

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages cloud storage operations across multiple providers."""

    def __init__(self, config: Config) -> None:
        """
        Initialize storage manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self._storage_providers: Dict[str, BaseCloudStorage] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize configured cloud storage providers."""
        # S3
        if self.config.storage.s3_bucket_name:
            try:
                from synth_agent.storage.s3_storage import S3Storage
                s3_config = {
                    "bucket_name": self.config.storage.s3_bucket_name,
                    "region_name": self.config.storage.s3_region,
                    "access_key_id": getattr(self.config.storage, "s3_access_key_id", None),
                    "secret_access_key": getattr(self.config.storage, "s3_secret_access_key", None),
                }
                self._storage_providers["s3"] = S3Storage(s3_config)
                logger.info("S3 storage provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize S3 storage: {e}")

        # GCS
        if self.config.storage.gcs_bucket_name:
            try:
                from synth_agent.storage.gcs_storage import GCSStorage
                gcs_config = {
                    "bucket_name": self.config.storage.gcs_bucket_name,
                    "project_id": getattr(self.config.storage, "gcs_project_id", None),
                    "credentials_path": getattr(self.config.storage, "gcs_credentials_path", None),
                }
                self._storage_providers["gcs"] = GCSStorage(gcs_config)
                logger.info("GCS storage provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize GCS storage: {e}")

        # Azure
        if self.config.storage.azure_container_name:
            try:
                from synth_agent.storage.azure_storage import AzureStorage
                azure_config = {
                    "container_name": self.config.storage.azure_container_name,
                    "connection_string": getattr(self.config.storage, "azure_connection_string", None),
                    "account_name": getattr(self.config.storage, "azure_account_name", None),
                    "account_key": getattr(self.config.storage, "azure_account_key", None),
                }
                self._storage_providers["azure"] = AzureStorage(azure_config)
                logger.info("Azure storage provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure storage: {e}")

    def upload_file(
        self,
        local_path: Path,
        remote_path: str,
        provider: str = "s3",
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload file to cloud storage.

        Args:
            local_path: Local file path
            remote_path: Remote file path/key
            provider: Storage provider (s3, gcs, azure)
            metadata: Optional metadata

        Returns:
            URL or URI of uploaded file

        Raises:
            StorageError: If provider not available or upload fails
        """
        provider = provider.lower()

        if provider not in self._storage_providers:
            available = ", ".join(self._storage_providers.keys())
            raise StorageError(
                f"Storage provider '{provider}' not configured. Available: {available}"
            )

        storage = self._storage_providers[provider]
        return storage.upload_file(local_path, remote_path, metadata)

    def download_file(
        self,
        remote_path: str,
        local_path: Path,
        provider: str = "s3"
    ) -> None:
        """
        Download file from cloud storage.

        Args:
            remote_path: Remote file path/key
            local_path: Local file path to save to
            provider: Storage provider (s3, gcs, azure)

        Raises:
            StorageError: If provider not available or download fails
        """
        provider = provider.lower()

        if provider not in self._storage_providers:
            available = ", ".join(self._storage_providers.keys())
            raise StorageError(
                f"Storage provider '{provider}' not configured. Available: {available}"
            )

        storage = self._storage_providers[provider]
        storage.download_file(remote_path, local_path)

    def get_public_url(
        self,
        remote_path: str,
        provider: str = "s3",
        expiration_seconds: int = 3600
    ) -> str:
        """
        Get public/signed URL for file.

        Args:
            remote_path: Remote file path/key
            provider: Storage provider (s3, gcs, azure)
            expiration_seconds: URL expiration time in seconds

        Returns:
            Public or signed URL

        Raises:
            StorageError: If provider not available or URL generation fails
        """
        provider = provider.lower()

        if provider not in self._storage_providers:
            available = ", ".join(self._storage_providers.keys())
            raise StorageError(
                f"Storage provider '{provider}' not configured. Available: {available}"
            )

        storage = self._storage_providers[provider]
        return storage.get_public_url(remote_path, expiration_seconds)

    def list_providers(self) -> list:
        """
        Get list of configured storage providers.

        Returns:
            List of provider names
        """
        return list(self._storage_providers.keys())

    def is_provider_available(self, provider: str) -> bool:
        """
        Check if storage provider is configured.

        Args:
            provider: Provider name (s3, gcs, azure)

        Returns:
            True if provider is available
        """
        return provider.lower() in self._storage_providers
