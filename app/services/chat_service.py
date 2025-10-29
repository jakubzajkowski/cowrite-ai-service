"""
Chat service module handling conversations and messages.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.auth_service import verify_user


class ChatService:
    """
    Class-based ChatService handling conversations and messages.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)

    async def create_conversation(self, user_token: str, title: Optional[str] = None):
        """
        Verify user and create a new conversation.
        """
        print("Creating conversation for user token:", user_token)
        user = await verify_user(user_token)
        if not user:
            raise ValueError("Invalid user token")

        conversation = await self.conversation_repo.create_conversation(
            user_id=user["id"], title=title
        )
        return conversation

    async def get_conversations_by_user(self, user_token: str):
        """
        Get all conversations for the verified user.
        """
        user = await verify_user(user_token)
        if not user:
            raise ValueError("Invalid user token")

        conversations = await self.conversation_repo.get_conversations_by_user(
            user_id=user["id"]
        )
        return conversations

    async def create_message(self, conversation_id: int, prompt: str, user_id: int):
        """
        Create a new message in a conversation.
        """
        message = await self.message_repo.create_message(
            conversation_id=conversation_id, user_id=user_id, prompt=prompt
        )
        return message

    async def update_message_response(
        self, message_id: int, response: str, status: str = "completed"
    ):
        """
        Update the response and status of a message.
        """
        message = await self.message_repo.update_message_response(
            message_id=message_id, response=response, status=status
        )
        return message

    async def get_messages_by_conversation(self, conversation_id: int) -> List:
        """
        Get all messages for a given conversation.
        """
        messages = await self.message_repo.get_messages_by_conversation(conversation_id)
        return messages
