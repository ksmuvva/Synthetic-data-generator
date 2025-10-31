"""AWS S3 cloud storage implementation."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from synth_agent.core.exceptions import StorageError
from synth_agent.storage.base import BaseCloudStorage

logger = logging.getLogger(__name__)


class S3Storage(BaseCloudStorage):
    """AWS S3 cloud storage provider."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize S3 storage.

        Args:
            config: S3 configuration
                - bucket_name: S3 bucket name
                - region_name: AWS region (optional)
                - access_key_id: AWS access key (optional, uses default credentials if not provided)
                - secret_access_key: AWS secret key (optional)
                - endpoint_url: Custom endpoint URL (optional, for S3-compatible services)
        """
        super().__init__(config)
        self.bucket_name = config.get("bucket_name")
        if not self.bucket_name:
            raise StorageError("S3 bucket_name is required")

        self.region_name = config.get("region_name", "us-east-1")
        self.endpoint_url = config.get("endpoint_url")

        # Initialize S3 client
        try:
            import boto3
            from botocore.exceptions import ClientError

            self.ClientError = ClientError

            # Create S3 client with optional credentials
            client_kwargs = {"region_name": self.region_name}

            if self.endpoint_url:
                client_kwargs["endpoint_url"] = self.endpoint_url

            if config.get("access_key_id") and config.get("secret_access_key"):
                client_kwargs["aws_access_key_id"] = config["access_key_id"]
                client_kwargs["aws_secret_access_key"] = config["secret_access_key"]

            self.s3_client = boto3.client("s3", **client_kwargs)
            logger.info(f"Initialized S3 storage for bucket: {self.bucket_name}")

        except ImportError:
            raise StorageError(
                "boto3 is required for S3 storage. Install with: pip install boto3"
            )

    def upload_file(self, local_path: Path, remote_path: str, metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Upload file to S3.

        Args:
            local_path: Local file path
            remote_path: S3 object key
            metadata: Optional metadata to attach

        Returns:
            S3 URI (s3://bucket/key)
        """
        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata

            self.s3_client.upload_file(
                str(local_path),
                self.bucket_name,
                remote_path,
                ExtraArgs=extra_args if extra_args else None
            )

            s3_uri = f"s3://{self.bucket_name}/{remote_path}"
            logger.info(f"Uploaded file to S3: {s3_uri}")
            return s3_uri

        except self.ClientError as e:
            raise StorageError(f"Failed to upload file to S3: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error uploading to S3: {e}")

    def download_file(self, remote_path: str, local_path: Path) -> None:
        """
        Download file from S3.

        Args:
            remote_path: S3 object key
            local_path: Local file path to save to
        """
        try:
            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            self.s3_client.download_file(
                self.bucket_name,
                remote_path,
                str(local_path)
            )

            logger.info(f"Downloaded file from S3: {remote_path} to {local_path}")

        except self.ClientError as e:
            raise StorageError(f"Failed to download file from S3: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error downloading from S3: {e}")

    def delete_file(self, remote_path: str) -> None:
        """
        Delete file from S3.

        Args:
            remote_path: S3 object key
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=remote_path
            )

            logger.info(f"Deleted file from S3: {remote_path}")

        except self.ClientError as e:
            raise StorageError(f"Failed to delete file from S3: {e}")

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in S3 bucket.

        Args:
            prefix: Prefix to filter files

        Returns:
            List of S3 object keys
        """
        try:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

            files = []
            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        files.append(obj["Key"])

            return files

        except self.ClientError as e:
            raise StorageError(f"Failed to list files in S3: {e}")

    def file_exists(self, remote_path: str) -> bool:
        """
        Check if file exists in S3.

        Args:
            remote_path: S3 object key

        Returns:
            True if file exists
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=remote_path)
            return True
        except self.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise StorageError(f"Failed to check file existence in S3: {e}")

    def get_public_url(self, remote_path: str, expiration_seconds: int = 3600) -> str:
        """
        Get presigned URL for S3 object.

        Args:
            remote_path: S3 object key
            expiration_seconds: URL expiration time in seconds

        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": remote_path},
                ExpiresIn=expiration_seconds
            )

            return url

        except self.ClientError as e:
            raise StorageError(f"Failed to generate presigned URL: {e}")
