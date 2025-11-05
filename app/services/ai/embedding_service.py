"""Service to handle text embeddings and storage in ChromaDB."""

import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai.chroma_client import ChromaClient
from app.services.files.s3_service import S3Client
from app.services.files.text_extraction_service import TextExtractionService
from app.repositories.chat_files_repository import ChatFileRepository


class EmbeddingService:
    """Service to handle text embeddings and storage in ChromaDB."""

    def __init__(
        self,
        chroma_client: ChromaClient,
        s3_client: S3Client,
        text_extractor_service: TextExtractionService,
        db: AsyncSession,
    ):
        self.chroma_client = chroma_client
        self.model = SentenceTransformer("intfloat/multilingual-e5-base")
        self.s3_client = s3_client
        self.text_extractor = text_extractor_service
        self.chat_file_repository = ChatFileRepository(db)

    def chunk_text(
        self, text: str, max_chunk_size: int = 1000, overlap: int = 200
    ) -> List[str]:
        """
        Split text into semantically meaningful chunks with overlap
        using LangChain RecursiveCharacterTextSplitter.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""],
        )

        chunks = splitter.split_text(text)
        chunks = [c.strip() for c in chunks if c.strip()]

        print("\n🔹 --- CHUNK PREVIEW --- 🔹")
        print(f"Total chunks created: {len(chunks)}\n")
        for i, chunk in enumerate(chunks, start=1):
            print(f"--- Chunk {i} ({len(chunk)} chars) ---")
            print(chunk)  # pokaz tylko pierwsze 500 znaków
            print("\n")

        return chunks

    async def add_file_embeddings(
        self, file_key: str, file_name: str, user_id: int, file_id: str
    ) -> dict:
        """Extract text from a file, generate embeddings, and store them in ChromaDB."""
        file_bytes = await self.s3_client.download_file_as_bytes(file_key)

        text = await self.text_extractor.extract_text(file_name, file_bytes)
        if not text.strip():
            raise ValueError(f"File {file_name} is empty.")

        chunks = self.chunk_text(text)
        if not chunks:
            raise ValueError("Failed to chunk text.")

        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(
                chunks, batch_size=16, convert_to_numpy=True
            ).tolist(),
        )

        ids = [f"{file_id}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "chunk_index": i,
                "s3_key": file_key,
            }
            for i in range(len(chunks))
        ]

        items = {
            "id": ids,
            "texts": chunks,
            "embeddings": embeddings,
            "metadata": metadatas,
        }

        await self.chroma_client.add(items)

        await self.chat_file_repository.update_status(file_id, "completed")

        return {"status": "ok", "chunks": len(chunks), "file_id": file_id}

    async def query_user_file_context(
        self, user_id: int, file_id: str, query_text: str, n_results: int = 3
    ) -> dict:
        """Search for similar text chunks in ChromaDB for a given user's file."""
        filters = {"user_id": user_id, "file_id": file_id}
        return await self.chroma_client.query(
            query_text=query_text, n_results=n_results, filters=filters
        )
