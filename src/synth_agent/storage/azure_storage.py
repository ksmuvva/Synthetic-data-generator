"""Azure Blob Storage implementation."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from synth_agent.core.exceptions import StorageError
from synth_agent.storage.base import BaseCloudStorage

logger = logging.getLogger(__name__)


class AzureStorage(BaseCloudStorage):
    """Azure Blob Storage provider."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize Azure Blob storage.

        Args:
            config: Azure configuration
                - container_name: Azure container name
                - connection_string: Azure connection string (optional)
                - account_name: Storage account name (optional, alternative to connection_string)
                - account_key: Storage account key (optional, alternative to connection_string)
        """
        super().__init__(config)
        self.container_name = config.get("container_name")
        if not self.container_name:
            raise StorageError("Azure container_name is required")

        self.connection_string = config.get("connection_string")
        self.account_name = config.get("account_name")
        self.account_key = config.get("account_key")

        # Initialize Azure Blob client
        try:
            from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
            from azure.core.exceptions import AzureError

            self.AzureError = AzureError
            self.generate_blob_sas = generate_blob_sas
            self.BlobSasPermissions = BlobSasPermissions

            # Create BlobServiceClient
            if self.connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
            elif self.account_name and self.account_key:
                account_url = f"https://{self.account_name}.blob.core.windows.net"
                from azure.storage.blob import BlobServiceClient
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url,
                    credential=self.account_key
                )
            else:
                raise StorageError(
                    "Either connection_string or (account_name + account_key) must be provided"
                )

            self.container_client = self.blob_service_client.get_container_client(
                self.container_name
            )

            # Create container if it doesn't exist
            try:
                self.container_client.create_container()
                logger.info(f"Created Azure container: {self.container_name}")
            except Exception:
                # Container already exists
                pass

            logger.info(f"Initialized Azure Blob storage for container: {self.container_name}")

        except ImportError:
            raise StorageError(
                "azure-storage-blob is required for Azure storage. Install with: pip install azure-storage-blob"
            )

    def upload_file(self, local_path: Path, remote_path: str, metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Upload file to Azure Blob.

        Args:
            local_path: Local file path
            remote_path: Azure blob name
            metadata: Optional metadata to attach

        Returns:
            Azure Blob URI
        """
        try:
            blob_client = self.container_client.get_blob_client(remote_path)

            with open(local_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True, metadata=metadata)

            blob_uri = blob_client.url
            logger.info(f"Uploaded file to Azure Blob: {blob_uri}")
            return blob_uri

        except self.AzureError as e:
            raise StorageError(f"Failed to upload file to Azure Blob: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error uploading to Azure Blob: {e}")

    def download_file(self, remote_path: str, local_path: Path) -> None:
        """
        Download file from Azure Blob.

        Args:
            remote_path: Azure blob name
            local_path: Local file path to save to
        """
        try:
            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            blob_client = self.container_client.get_blob_client(remote_path)

            with open(local_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())

            logger.info(f"Downloaded file from Azure Blob: {remote_path} to {local_path}")

        except self.AzureError as e:
            raise StorageError(f"Failed to download file from Azure Blob: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error downloading from Azure Blob: {e}")

    def delete_file(self, remote_path: str) -> None:
        """
        Delete file from Azure Blob.

        Args:
            remote_path: Azure blob name
        """
        try:
            blob_client = self.container_client.get_blob_client(remote_path)
            blob_client.delete_blob()

            logger.info(f"Deleted file from Azure Blob: {remote_path}")

        except self.AzureError as e:
            raise StorageError(f"Failed to delete file from Azure Blob: {e}")

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in Azure Blob container.

        Args:
            prefix: Prefix to filter files

        Returns:
            List of Azure blob names
        """
        try:
            blob_list = self.container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blob_list]

        except self.AzureError as e:
            raise StorageError(f"Failed to list files in Azure Blob: {e}")

    def file_exists(self, remote_path: str) -> bool:
        """
        Check if file exists in Azure Blob.

        Args:
            remote_path: Azure blob name

        Returns:
            True if file exists
        """
        try:
            blob_client = self.container_client.get_blob_client(remote_path)
            return blob_client.exists()

        except self.AzureError as e:
            raise StorageError(f"Failed to check file existence in Azure Blob: {e}")

    def get_public_url(self, remote_path: str, expiration_seconds: int = 3600) -> str:
        """
        Get SAS URL for Azure Blob.

        Args:
            remote_path: Azure blob name
            expiration_seconds: URL expiration time in seconds

        Returns:
            SAS URL
        """
        try:
            if not self.account_name or not self.account_key:
                raise StorageError(
                    "account_name and account_key are required to generate SAS URLs"
                )

            # Generate SAS token
            sas_token = self.generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=remote_path,
                account_key=self.account_key,
                permission=self.BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(seconds=expiration_seconds)
            )

            # Construct SAS URL
            blob_client = self.container_client.get_blob_client(remote_path)
            sas_url = f"{blob_client.url}?{sas_token}"

            return sas_url

        except self.AzureError as e:
            raise StorageError(f"Failed to generate SAS URL: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error generating SAS URL: {e}")
