"""Storage service: S3 upload, download, and presigned URL generation."""

import structlog
import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = structlog.get_logger(__name__)


class StorageService:
    """Wraps AWS S3 for file storage operations."""

    def __init__(self) -> None:
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION,
        )
        self.bucket = settings.AWS_S3_BUCKET

    async def upload(self, key: str, data: bytes, content_type: str = "audio/wav") -> str:
        """Upload a file to S3.

        Args:
            key: The S3 object key (path).
            data: File content bytes.
            content_type: MIME type of the file.

        Returns:
            The S3 URL of the uploaded file.
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
            url = f"https://{self.bucket}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{key}"
            logger.info("s3_upload_success", key=key)
            return url
        except ClientError as e:
            logger.error("s3_upload_failed", key=key, error=str(e))
            raise

    async def download(self, key: str) -> bytes:
        """Download a file from S3.

        Args:
            key: The S3 object key (path).

        Returns:
            File content bytes.
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            data = response["Body"].read()
            logger.info("s3_download_success", key=key)
            return data
        except ClientError as e:
            logger.error("s3_download_failed", key=key, error=str(e))
            raise

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary access to an S3 object.

        Args:
            key: The S3 object key (path).
            expires_in: URL expiration time in seconds (default: 1 hour).

        Returns:
            Presigned URL string.
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error("s3_presigned_url_failed", key=key, error=str(e))
            raise
