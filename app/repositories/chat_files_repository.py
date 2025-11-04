from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.models.chat_file import ChatFile


class ChatFileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        conversation_id: int,
        user_id: Optional[int],
        filename: str,
        file_type: str,
        size: int,
        key: str,
        storage_path: str,
    ) -> ChatFile:
        chat_file = ChatFile(
            conversation_id=conversation_id,
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            size=size,
            storage_path=storage_path,
            key=key,
        )
        self.session.add(chat_file)
        await self.session.commit()
        await self.session.refresh(chat_file)
        return chat_file

    async def get_by_id(self, file_id: str) -> Optional[ChatFile]:
        result = await self.session.execute(
            select(ChatFile).where(ChatFile.id == file_id)
        )
        return result.scalars().first()

    async def list_by_conversation(self, conversation_id: int) -> List[ChatFile]:
        result = await self.session.execute(
            select(ChatFile).where(ChatFile.conversation_id == conversation_id)
        )
        return result.scalars().all()

    async def list_user_files(
        self, conversation_id: int, max_files: int = 3
    ) -> List[ChatFile]:
        stmt = (
            select(ChatFile)
            .where(
                ChatFile.conversation_id == conversation_id,
                ChatFile.user_id.isnot(None),
            )
            .order_by(ChatFile.created_at.asc())
            .limit(max_files)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, file_id: str) -> bool:
        result = await self.session.execute(
            delete(ChatFile).where(ChatFile.id == file_id).returning(ChatFile.id)
        )
        deleted = result.scalar()
        if deleted:
            await self.session.commit()
            return True
        return False

    async def update_status(self, file_id: str, status: str) -> Optional[ChatFile]:
        chat_file = await self.get_by_id(file_id)
        if chat_file:
            chat_file.status = status
            self.session.add(chat_file)
            await self.session.commit()
            await self.session.refresh(chat_file)
            return chat_file
        return None
