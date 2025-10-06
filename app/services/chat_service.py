"""
Functional ChatService using ConversationRepository.
Handles conversation creation and user verification.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.conversation_repository import ConversationRepository
from app.services.auth_service import verify_user


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
