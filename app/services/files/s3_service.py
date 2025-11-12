"""Asynchronous service for interacting with AWS S3."""

from typing import Union, AsyncGenerator
import io
import aioboto3
from app.core.settings import settings


class S3Client:
    """Async client for interacting with AWS S3."""

    def __init__(self):
        """Initialize the async S3 client with settings."""
        self.session = aioboto3.Session()
        self.bucket = settings.aws_s3_bucket
        self.endpoint_url = settings.s3_endpoint_url
        self.region = settings.aws_region
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key

    async def _get_client(self) -> AsyncGenerator:
        """Async context manager for S3 client."""
        async with self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as s3:
            yield s3

    async def create_bucket_if_not_exists(self):
        """Create the S3 bucket if it does not already exist."""
        async for s3 in self._get_client():
            response = await s3.list_buckets()
            buckets = [b["Name"] for b in response.get("Buckets", [])]
            if self.bucket not in buckets:
                await s3.create_bucket(Bucket=self.bucket)

    async def upload_object_to_s3(
        self,
        obj: Union[bytes, io.BytesIO],
        key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload any object (bytes or BytesIO) to S3 and return the S3 path."""
        if isinstance(obj, bytes):
            obj = io.BytesIO(obj)

        async for s3 in self._get_client():
            await s3.upload_fileobj(
                Fileobj=obj,
                Bucket=self.bucket,
                Key=key,
                ExtraArgs={"ContentType": content_type},
            )

        return f"s3://{self.bucket}/{key}"

    async def download_file_as_bytes(self, key: str, bucket: str) -> bytes:
        """Download an S3 object as bytes."""
        async for s3 in self._get_client():
            response = await s3.get_object(Bucket=bucket, Key=key)
            async with response["Body"] as stream:
                content = await stream.read()

        return content
