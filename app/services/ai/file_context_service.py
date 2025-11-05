""" "Service to extract and compile context from user-uploaded files stored in S3."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.embedding_service import EmbeddingService
from app.repositories.chat_files_repository import ChatFileRepository


class FileContextService:
    """Service to compile context from embeddings of files related to a conversation."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        db: AsyncSession,
    ):
        self.embedding_service = embedding_service
        self.db = db
        self.chat_file_repo = ChatFileRepository(db)

    async def get_external_file_context(
        self,
        conversation_id: int,
        user_id: int,
        query_text: str,
        max_files: int = 50,
        max_tokens: int = 10000,
        top_k: int = 3,
    ) -> str:
        """
        Retrieve relevant semantic context for a query based on embeddings
        from all files in the given conversation.
        """
        chat_files = await self.chat_file_repo.list_user_files(
            conversation_id, max_files
        )

        if not chat_files:
            return ""

        external_texts: list[str] = []

        print(f"Found {len(chat_files)} files for context retrieval.")

        for f in chat_files:
            result = await self.embedding_service.query_user_file_context(
                user_id=user_id,
                file_id=str(f.id),
                query_text=query_text,
                n_results=top_k,
            )

            docs = result.get("documents", [[]])[0]

            if not docs:
                continue

            text = f"📄 File: {f.filename}\n" + "\n---\n".join(docs)
            external_texts.append(text)

        if not external_texts:
            return ""

        context = "\n\n===========================\n\n".join(external_texts)

        if len(context) > max_tokens:
            context = context[:max_tokens]

        return context
