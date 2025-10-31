"""Google Cloud Storage implementation."""

import logging
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from synth_agent.core.exceptions import StorageError
from synth_agent.storage.base import BaseCloudStorage

logger = logging.getLogger(__name__)


class GCSStorage(BaseCloudStorage):
    """Google Cloud Storage provider."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize GCS storage.

        Args:
            config: GCS configuration
                - bucket_name: GCS bucket name
                - project_id: GCP project ID (optional)
                - credentials_path: Path to service account JSON (optional)
        """
        super().__init__(config)
        self.bucket_name = config.get("bucket_name")
        if not self.bucket_name:
            raise StorageError("GCS bucket_name is required")

        self.project_id = config.get("project_id")
        self.credentials_path = config.get("credentials_path")

        # Initialize GCS client
        try:
            from google.cloud import storage
            from google.cloud.exceptions import GoogleCloudError

            self.GoogleCloudError = GoogleCloudError

            # Create client with optional credentials
            client_kwargs = {}
            if self.project_id:
                client_kwargs["project"] = self.project_id

            if self.credentials_path:
                from google.oauth2 import service_account
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.storage_client = storage.Client(credentials=credentials, **client_kwargs)
            else:
                # Use default credentials
                self.storage_client = storage.Client(**client_kwargs)

            self.bucket = self.storage_client.bucket(self.bucket_name)
            logger.info(f"Initialized GCS storage for bucket: {self.bucket_name}")

        except ImportError:
            raise StorageError(
                "google-cloud-storage is required for GCS storage. Install with: pip install google-cloud-storage"
            )

    def upload_file(self, local_path: Path, remote_path: str, metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Upload file to GCS.

        Args:
            local_path: Local file path
            remote_path: GCS blob name
            metadata: Optional metadata to attach

        Returns:
            GCS URI (gs://bucket/blob)
        """
        try:
            blob = self.bucket.blob(remote_path)

            # Set metadata if provided
            if metadata:
                blob.metadata = metadata

            blob.upload_from_filename(str(local_path))

            gcs_uri = f"gs://{self.bucket_name}/{remote_path}"
            logger.info(f"Uploaded file to GCS: {gcs_uri}")
            return gcs_uri

        except self.GoogleCloudError as e:
            raise StorageError(f"Failed to upload file to GCS: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error uploading to GCS: {e}")

    def download_file(self, remote_path: str, local_path: Path) -> None:
        """
        Download file from GCS.

        Args:
            remote_path: GCS blob name
            local_path: Local file path to save to
        """
        try:
            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            blob = self.bucket.blob(remote_path)
            blob.download_to_filename(str(local_path))

            logger.info(f"Downloaded file from GCS: {remote_path} to {local_path}")

        except self.GoogleCloudError as e:
            raise StorageError(f"Failed to download file from GCS: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error downloading from GCS: {e}")

    def delete_file(self, remote_path: str) -> None:
        """
        Delete file from GCS.

        Args:
            remote_path: GCS blob name
        """
        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()

            logger.info(f"Deleted file from GCS: {remote_path}")

        except self.GoogleCloudError as e:
            raise StorageError(f"Failed to delete file from GCS: {e}")

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in GCS bucket.

        Args:
            prefix: Prefix to filter files

        Returns:
            List of GCS blob names
        """
        try:
            blobs = self.storage_client.list_blobs(self.bucket_name, prefix=prefix)
            return [blob.name for blob in blobs]

        except self.GoogleCloudError as e:
            raise StorageError(f"Failed to list files in GCS: {e}")

    def file_exists(self, remote_path: str) -> bool:
        """
        Check if file exists in GCS.

        Args:
            remote_path: GCS blob name

        Returns:
            True if file exists
        """
        try:
            blob = self.bucket.blob(remote_path)
            return blob.exists()

        except self.GoogleCloudError as e:
            raise StorageError(f"Failed to check file existence in GCS: {e}")

    def get_public_url(self, remote_path: str, expiration_seconds: int = 3600) -> str:
        """
        Get signed URL for GCS blob.

        Args:
            remote_path: GCS blob name
            expiration_seconds: URL expiration time in seconds

        Returns:
            Signed URL
        """
        try:
            blob = self.bucket.blob(remote_path)

            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(seconds=expiration_seconds),
                method="GET"
            )

            return url

        except self.GoogleCloudError as e:
            raise StorageError(f"Failed to generate signed URL: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error generating signed URL: {e}")
