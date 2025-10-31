import re
from sentence_transformers import SentenceTransformer
from app.services.ai.chroma_client import ChromaClient
from app.services.files.s3_service import S3Client
from app.services.files.text_extraction_service import TextExtractionService


class EmbeddingService:
    def __init__(
        self,
        chroma_client: ChromaClient,
        s3_client: S3Client,
        text_extractor_service: TextExtractionService,
    ):
        self.chroma_client = chroma_client
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.s3_client = s3_client
        self.text_extractor = text_extractor_service

    def chunk_text(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return sentences

    async def add_file_embeddings(
        self, file_key: str, file_name: str, user_id: int, file_id: str
    ) -> dict:
        file_bytes = self.s3_client.download_file_as_bytes(file_key)

        text = await self.text_extractor.extract_text(file_name, file_bytes)
        if not text.strip():
            raise ValueError(f"Plik {file_name} nie zawiera tekstu.")

        chunks = self.chunk_text(text)
        if not chunks:
            raise ValueError("Nie udało się podzielić tekstu na fragmenty.")

        embeddings = self.model.encode(
            chunks, batch_size=16, convert_to_numpy=True
        ).tolist()

        file_id = file_id
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

        self.chroma_client.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return {"status": "ok", "chunks": len(chunks), "file_id": file_id}
