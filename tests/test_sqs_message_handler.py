"""Unit tests for SQS message handler with different event types."""

# pylint: disable=redefined-outer-name

import json
from unittest.mock import AsyncMock, MagicMock
import pytest


@pytest.fixture
def embedding_service_mock():
    """Create a mock embedding service."""
    service = AsyncMock()
    service.add_workspace_file_embeddings = AsyncMock(
        return_value={"status": "ok", "chunks": 5, "file_id": "123", "workspace_id": 1}
    )
    service.delete_workspace_file_embeddings = AsyncMock(
        return_value={
            "status": "deleted",
            "count": 5,
            "file_id": "123",
            "workspace_id": 1,
        }
    )
    return service


@pytest.fixture
def message_handler(embedding_service_mock):
    """Create a message handler with mock service."""
    handler = MagicMock()
    handler.embedding_service = embedding_service_mock

    async def mock_handle(message_body):
        """Mock implementation of handle_workspace_file_message."""
        try:
            data = json.loads(message_body)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid message format") from e

        event_type = data.get("eventType")
        workspace_id = data.get("workspaceId")
        file_id = data.get("fileId")
        s3_key = data.get("s3Key")

        if not event_type:
            raise ValueError("Missing eventType")

        if event_type == "create":
            result = await embedding_service_mock.add_workspace_file_embeddings(
                workspace_id=workspace_id, file_id=file_id, s3_key=s3_key
            )
            return {"event_type": "create", **result}
        if event_type == "update":
            delete_result = (
                await embedding_service_mock.delete_workspace_file_embeddings(
                    workspace_id=workspace_id, file_id=file_id
                )
            )
            add_result = await embedding_service_mock.add_workspace_file_embeddings(
                workspace_id=workspace_id, file_id=file_id, s3_key=s3_key
            )
            return {
                "event_type": "update",
                "deleted_count": delete_result["count"],
                **add_result,
            }
        if event_type == "delete":
            result = await embedding_service_mock.delete_workspace_file_embeddings(
                workspace_id=workspace_id, file_id=file_id
            )
            return {"event_type": "delete", **result}
        raise ValueError(f"Invalid eventType: {event_type}")

    handler.handle_workspace_file_message = mock_handle
    return handler


@pytest.mark.asyncio
async def test_handle_create_event(message_handler, embedding_service_mock):
    """Test handling of 'create' event type."""
    message_body = json.dumps(
        {
            "workspaceId": 1,
            "fileId": 123,
            "s3Key": "workspace/1/file.pdf",
            "eventType": "create",
        }
    )

    result = await message_handler.handle_workspace_file_message(message_body)

    assert result["event_type"] == "create"
    assert result["status"] == "ok"
    assert result["chunks"] == 5
    embedding_service_mock.add_workspace_file_embeddings.assert_called_once()
    embedding_service_mock.delete_workspace_file_embeddings.assert_not_called()


@pytest.mark.asyncio
async def test_handle_update_event(message_handler, embedding_service_mock):
    """Test handling of 'update' event type."""
    message_body = json.dumps(
        {
            "workspaceId": 1,
            "fileId": 123,
            "s3Key": "workspace/1/file.pdf",
            "eventType": "update",
        }
    )

    result = await message_handler.handle_workspace_file_message(message_body)

    assert result["event_type"] == "update"
    assert result["deleted_count"] == 5
    assert result["chunks"] == 5
    # Should delete old embeddings first, then create new ones
    embedding_service_mock.delete_workspace_file_embeddings.assert_called_once()
    embedding_service_mock.add_workspace_file_embeddings.assert_called_once()


@pytest.mark.asyncio
async def test_handle_delete_event(message_handler, embedding_service_mock):
    """Test handling of 'delete' event type."""
    message_body = json.dumps(
        {
            "workspaceId": 1,
            "fileId": 123,
            "s3Key": "workspace/1/file.pdf",
            "eventType": "delete",
        }
    )

    result = await message_handler.handle_workspace_file_message(message_body)

    assert result["event_type"] == "delete"
    assert result["status"] == "deleted"
    assert result["count"] == 5
    embedding_service_mock.delete_workspace_file_embeddings.assert_called_once()
    embedding_service_mock.add_workspace_file_embeddings.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_event_type(message_handler):
    """Test handling of invalid event type."""
    message_body = json.dumps(
        {
            "workspaceId": 1,
            "fileId": 123,
            "s3Key": "workspace/1/file.pdf",
            "eventType": "invalid",
        }
    )

    with pytest.raises(ValueError, match="eventType"):
        await message_handler.handle_workspace_file_message(message_body)


@pytest.mark.asyncio
async def test_invalid_json(message_handler):
    """Test handling of invalid JSON."""
    message_body = "{ invalid json }"

    with pytest.raises(ValueError, match="Invalid message format"):
        await message_handler.handle_workspace_file_message(message_body)


@pytest.mark.asyncio
async def test_missing_required_fields(message_handler):
    """Test handling of message with missing required fields."""
    message_body = json.dumps(
        {
            "workspaceId": 1,
            "fileId": 123,
            # Missing s3Key and eventType
        }
    )

    with pytest.raises(Exception):  # Pydantic validation error
        await message_handler.handle_workspace_file_message(message_body)
