"""Service for interacting with AWS S3."""

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


s3_service = S3Client()
