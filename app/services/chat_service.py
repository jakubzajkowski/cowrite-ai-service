"""
Functional ChatService using ConversationRepository.
Handles conversation creation and user verification.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.conversation_repository import ConversationRepository
from app.services.auth_service import verify_user
from app.repositories.message_repository import MessageRepository


# -------------------------
# Conversation functions
# -------------------------
async def create_conversation(
    db: AsyncSession, user_token: str, title: str | None = None
):
    """
    Verify user and create a new conversation.
    """
    print("Creating conversation for user token:", user_token)
    user = await verify_user(user_token)
    if not user:
        raise ValueError("Invalid user token")

    repo = ConversationRepository(db)
    conversation = await repo.create_conversation(user_id=user["id"], title=title)
    return conversation


async def get_conversations_by_user(db: AsyncSession, user_token: str):
    """
    Get all conversations for the verified user.
    """
    user = await verify_user(user_token)
    if not user:
        raise ValueError("Invalid user token")

    repo = ConversationRepository(db)
    conversations = await repo.get_conversations_by_user(user_id=user["id"])
    return conversations


# -------------------------
# Message functions
# -------------------------
async def create_message(
    db: AsyncSession, conversation_id: int, prompt: str, user_id: int
):
    """
    Verify user and create a new message in a conversation.
    """
    repo = MessageRepository(db)
    message = await repo.create_message(
        conversation_id=conversation_id, user_id=user_id, prompt=prompt
    )
    return message


async def update_message_response(
    db: AsyncSession, message_id: int, response: str, status: str = "completed"
):
    """
    Update the response and status of a message.
    """
    repo = MessageRepository(db)
    message = await repo.update_message_response(
        message_id=message_id, response=response, status=status
    )
    return message


async def get_messages_by_conversation(db: AsyncSession, conversation_id: int):
    """
    Get all messages for a given conversation.
    """
    repo = MessageRepository(db)
    messages = await repo.get_messages_by_conversation(conversation_id)
    return messages
