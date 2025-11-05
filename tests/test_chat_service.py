"""Unit tests for ChatService."""

# pylint: disable=import-outside-toplevel

from unittest.mock import AsyncMock, MagicMock
import pytest


@pytest.mark.asyncio
async def test_chat_service_creates_message():
    """Test ChatService.create_message saves message to database."""
    from app.services.chat.chat_service import ChatService

    # Mock database session
    mock_db = AsyncMock()

    # Mock the repository method
    mock_message = MagicMock()
    mock_message.id = 1
    mock_message.prompt = "Hello"
    mock_message.conversation_id = 1

    # Create service
    service = ChatService(db=mock_db)
    service.message_repo.create_message = AsyncMock(return_value=mock_message)

    # Test message creation
    result = await service.create_message(
        conversation_id=1, prompt="Hello", user_id=123
    )

    # Verify
    assert result.prompt == "Hello"
    service.message_repo.create_message.assert_called_once_with(
        conversation_id=1, user_id=123, prompt="Hello"
    )


@pytest.mark.asyncio
async def test_chat_service_updates_message_response():
    """Test ChatService updates message response."""
    from app.services.chat.chat_service import ChatService

    # Mock database session
    mock_db = AsyncMock()

    # Mock updated message
    mock_message = MagicMock()
    mock_message.id = 1
    mock_message.response = "AI response"
    mock_message.status = "completed"

    # Create service
    service = ChatService(db=mock_db)
    service.message_repo.update_message_response = AsyncMock(return_value=mock_message)

    # Update message
    result = await service.update_message_response(message_id=1, response="AI response")

    # Verify
    assert result.response == "AI response"
    assert result.status == "completed"
    service.message_repo.update_message_response.assert_called_once()


@pytest.mark.asyncio
async def test_chat_service_gets_messages():
    """Test ChatService retrieves messages for a conversation."""
    from app.services.chat.chat_service import ChatService

    # Mock database session
    mock_db = AsyncMock()

    # Mock messages
    mock_messages = [
        MagicMock(id=1, prompt="Hello", response="Hi"),
        MagicMock(id=2, prompt="How are you?", response="Good"),
    ]

    # Create service
    service = ChatService(db=mock_db)
    service.message_repo.get_messages_by_conversation = AsyncMock(
        return_value=mock_messages
    )

    # Get messages
    messages = await service.get_messages_by_conversation(conversation_id=1)

    # Verify
    assert len(messages) == 2
    assert messages[0].prompt == "Hello"
    service.message_repo.get_messages_by_conversation.assert_called_once_with(1)
