"""Service for interacting with AWS S3."""

from typing import Union
import io
import boto3
from app.core.settings import settings


class S3Client:
    """Client for interacting with AWS S3."""

    def __init__(self):
        """Initialize the S3 client with settings."""

        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )

    def create_bucket_if_not_exists(self):
        """Create the S3 bucket if it does not already exist."""

        buckets = [b["Name"] for b in self.client.list_buckets()["Buckets"]]
        if settings.aws_s3_bucket not in buckets:
            self.client.create_bucket(Bucket=settings.aws_s3_bucket)

    def upload_object_to_s3(
        self,
        obj: Union[bytes, io.BytesIO],
        key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload any object (bytes or BytesIO) to S3.

        Args:
            obj: bytes or BytesIO
            key: object key in S3
            bucket: S3 bucket name
            content_type: MIME type

        Returns:
            str: S3 path/url
        """
        if isinstance(obj, bytes):
            obj = io.BytesIO(obj)

        self.client.upload_fileobj(
            Fileobj=obj,
            Bucket=settings.aws_s3_bucket,
            Key=key,
            ExtraArgs={"ContentType": content_type},
        )

        return f"s3://{settings.aws_s3_bucket}/{key}"

    def get_object_content_as_text(self, key: str) -> str:
        """
        Get the content of an S3 object as UTF-8 text.

        Args:
            key: object key in S3

        Returns:
            str: object content as text
        """
        response = self.client.get_object(Bucket=settings.aws_s3_bucket, Key=key)
        content = response["Body"].read()
        return content.decode("utf-8")


s3_service = S3Client()
