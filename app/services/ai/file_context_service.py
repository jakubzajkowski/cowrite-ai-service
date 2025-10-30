""" "Service to extract and compile context from user-uploaded files stored in S3."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.files.s3_service import S3Client
from app.repositories.chat_files_repository import ChatFileRepository
from app.services.files.text_extraction_service import TextExtractionService


class FileContextService:
    """Service to extract and compile context from user-uploaded files stored in S3."""

    def __init__(
        self,
        text_extractor: TextExtractionService,
        s3_client: S3Client,
        db: AsyncSession,
    ):
        self.text_extractor = text_extractor
        self.s3_client = s3_client
        self.db = db
        self.chat_file_repo = ChatFileRepository(db)

    """Get compiled context from external files for a conversation."""

    async def get_external_file_context(
        self, conversation_id: int, max_files: int = 3, max_tokens: int = 10000
    ) -> str:

        chat_files = await self.chat_file_repo.list_user_files(
            conversation_id, max_files
        )

        external_texts: list[str] = []

        for f in chat_files:
            content_bytes = self.s3_client.download_file_as_bytes(f.key)
            extracted_text = await self.text_extractor.extract_text(
                f.filename, content_bytes
            )
            if extracted_text:
                external_texts.append(f"File {f.filename}:\n{extracted_text}")

        context = "\n---\n".join(external_texts)
        if len(context) > max_tokens:
            context = context[:max_tokens]

        return context
