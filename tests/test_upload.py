"""Unit tests for upload service."""

# pylint: disable=import-outside-toplevel

from unittest.mock import AsyncMock, MagicMock, patch
import pytest


@pytest.mark.asyncio
async def test_upload_service_saves_metadata():
    """Test UploadService saves file metadata to database."""
    from app.services.files.upload_service import UploadService
    from fastapi import UploadFile

    # Mock S3 client
    mock_s3 = MagicMock()
    mock_s3.upload_object_to_s3 = AsyncMock(return_value="s3://bucket/test.pdf")

    # Mock database session
    mock_db = AsyncMock()

    # Create service
    service = UploadService(s3_client=mock_s3)

    # Mock file
    file_content = b"fake pdf content"
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.read = AsyncMock(return_value=file_content)

    # Mock repository
    mock_chat_file = MagicMock()
    mock_chat_file.id = 1
    mock_chat_file.filename = "test.pdf"

    with patch(
        "app.services.files.upload_service.ChatFileRepository"
    ) as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=mock_chat_file)
        mock_repo_class.return_value = mock_repo

        # Test upload
        result = await service.upload_file_and_save_metadata(
            session=mock_db, file=mock_file, conversation_id=1, user_id=123
        )

        # Verify
        assert result.filename == "test.pdf"
        mock_s3.upload_object_to_s3.assert_called_once()
        mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_s3_client_initialization():
    """Test S3Client initializes with settings."""
    from app.services.files.s3_service import S3Client

    # Create client
    client = S3Client()

    # Verify properties exist
    assert client.session is not None
    assert client.bucket is not None


@pytest.mark.asyncio
async def test_s3_client_upload_object():
    """Test S3Client upload_object_to_s3 method."""
    from app.services.files.s3_service import S3Client

    with patch("app.services.files.s3_service.aioboto3.Session") as mock_session_class:
        # Mock S3 client
        mock_s3_client = AsyncMock()
        mock_s3_client.upload_fileobj = AsyncMock()

        # Mock session context manager
        mock_session = MagicMock()
        mock_session.client = MagicMock()
        mock_session.client.return_value.__aenter__ = AsyncMock(
            return_value=mock_s3_client
        )
        mock_session.client.return_value.__aexit__ = AsyncMock()

        mock_session_class.return_value = mock_session

        # Create client and upload
        client = S3Client()
        result = await client.upload_object_to_s3(
            obj=b"test content", key="test.pdf", content_type="application/pdf"
        )

        # Verify
        assert "s3://" in result
        assert "test.pdf" in result
