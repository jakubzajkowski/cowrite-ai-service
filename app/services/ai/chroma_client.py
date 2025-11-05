"""Async-safe client to interact with ChromaDB for storing and querying text embeddings."""

import asyncio
from chromadb import HttpClient
from sentence_transformers import SentenceTransformer
from app.core.settings import settings


class ChromaClient:
    """Async-safe client for interacting with ChromaDB."""

    def __init__(
        self,
        collection_name: str = "document",
        embedding_model: str = "intfloat/multilingual-e5-base",
    ):
        self.host = settings.chroma_host
        self.port = settings.chroma_port
        self.collection_name = collection_name

        self.model = SentenceTransformer(embedding_model)
        self.client = HttpClient(host=self.host, port=self.port)
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        existing = [c.name for c in self.client.list_collections()]
        if self.collection_name in existing:
            return self.client.get_collection(self.collection_name)
        return self.client.create_collection(name=self.collection_name)

    async def add(self, items: dict):
        """Add documents asynchronously."""
        if not items:
            raise ValueError("Item cannot be empty.")

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: self.collection.add(
                ids=items["id"],
                embeddings=items["embeddings"],
                documents=items["texts"],
                metadatas=items["metadata"],
            ),
        )

    async def query(
        self, query_text: str, n_results: int = 3, filters: dict | None = None
    ):
        """Query the collection asynchronously with optional metadata filters."""
        if not query_text.strip():
            raise ValueError("Query text cannot be empty.")

        query_vec = await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.model.encode([query_text]).tolist()
        )

        where = None
        if filters:
            where = {"$and": [{k: {"$eq": v}} for k, v in filters.items()]}

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.collection.query(
                query_embeddings=query_vec,
                n_results=n_results,
                where=where,
            ),
        )
        return results

    async def delete(self, ids: list[str]):
        """Delete documents asynchronously."""
        if not ids:
            raise ValueError("IDs list cannot be empty.")

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: self.collection.delete(ids=ids))

    async def list_collections(self) -> list[str]:
        """List all available collections asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: [c.name for c in self.client.list_collections()]
        )
