from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, conversation_id: int, user_id: str, prompt: str):
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            prompt=prompt,
            status="pending",
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def update_message_response(
        self, message_id: int, response: str, status: str = "completed"
    ):
        result = await self.db.execute(select(Message).where(Message.id == message_id))
        message = result.scalars().first()
        if message:
            message.response = response
            message.status = status
            await self.db.commit()
            await self.db.refresh(message)
        return message

    async def get_messages_by_conversation(self, conversation_id: int):
        result = await self.db.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        return result.scalars().all()
