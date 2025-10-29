"""Service for uploading files to S3 and saving metadata in the database."""

from uuid import uuid4
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.chat_files_repository import ChatFileRepository
from app.services.s3_service import S3Client


class UploadService:
    """Service for uploading files to S3 and saving metadata in the database."""

    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client

    async def upload_file_and_save_metadata(
        self,
        session: AsyncSession,
        file: UploadFile,
        conversation_id: int,
        user_id: int,
    ):
        """
        Upload a file to S3 and save its metadata in the database.

        Args:
            session: Async SQLAlchemy session
            file: FastAPI UploadFile
            conversation_id: ID of the conversation
            user_id: ID of the user uploading the file

        Returns:
            ChatFile: created ChatFile record
        """
        key = f"{uuid4()}_{file.filename}"
        content = await file.read()

        s3_path = self.s3_client.upload_object_to_s3(
            obj=content,
            key=key,
            content_type=file.content_type or "application/octet-stream",
        )

        repo = ChatFileRepository(session)
        chat_file = await repo.create(
            conversation_id=conversation_id,
            user_id=user_id,
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream",
            size=len(content),
            key=key,
            storage_path=s3_path,
        )

        return chat_file
