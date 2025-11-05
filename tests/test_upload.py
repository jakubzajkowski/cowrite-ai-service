"""Unit tests for file upload endpoint with mocked dependencies."""

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {"id": 123, "email": "test@example.com"}


@pytest.fixture
def mock_file_id():
    """Mock UUID for file ID."""
    return uuid.uuid4()


@pytest.fixture
def mock_upload_service(mock_file_id):  # pylint: disable=redefined-outer-name
    """Mock UploadService for file operations."""
    service = AsyncMock()

    mock_file = MagicMock()
    mock_file.id = mock_file_id
    mock_file.key = "s3://bucket/test.pdf"
    mock_file.filename = "test.pdf"
    mock_file.status = "uploaded"
    mock_file.file_type = "application/pdf"
    mock_file.size = 1024

    service.upload_file_and_save_metadata.return_value = mock_file
    service.get_file_status.return_value = mock_file

    return service


@pytest.mark.asyncio
async def test_upload_file_unauthorized(client):
    """POST /conversations/{id}/upload should return 401 without authentication."""
    # No auth mock - should fail
    file_content = b"fake pdf content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}

    response = await client.post("/conversations/1/upload", files=files)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_file_status_success(
    fastapi_app,  # pylint: disable=redefined-outer-name
    client,
    mock_upload_service,  # pylint: disable=redefined-outer-name
    mock_file_id,  # pylint: disable=redefined-outer-name
):
    """GET /conversations/upload/status/{file_id} should return file processing status."""
    # Import at top level to avoid pylint warning
    from app.api.v1 import upload  # pylint: disable=import-outside-toplevel

    # Mock upload service dependency
    async def mock_get_upload_service():
        return mock_upload_service

    fastapi_app.dependency_overrides[upload.get_upload_service] = (
        mock_get_upload_service
    )

    try:
        response = await client.get(f"/conversations/upload/status/{mock_file_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["fileId"] == str(mock_file_id)
        assert data["status"] == "uploaded"
    finally:
        fastapi_app.dependency_overrides.clear()
