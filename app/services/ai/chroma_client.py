from chromadb import HttpClient
from sentence_transformers import SentenceTransformer
from app.core.settings import settings


class ChromaClient:
    """
    Client to interact with ChromaDB for storing and querying text embeddings.
    """

    def __init__(
        self,
        collection_name: str = "docs",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self.host = settings.chroma_host
        self.port = settings.chroma_port
        self.collection_name = collection_name

        self.model = SentenceTransformer(embedding_model)

        self.client = HttpClient(host=self.host, port=self.port)
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Returns the collection (creates it if it doesn't exist)."""
        existing = [c.name for c in self.client.list_collections()]
        if self.collection_name in existing:
            return self.client.get_collection(self.collection_name)
        return self.client.create_collection(name=self.collection_name)

    def query(self, query_text: str, n_results: int = 3):
        """Searches for the most similar documents for the query."""
        if not query_text.strip():
            raise ValueError("Query text cannot be empty.")

        query_vec = self.model.encode([query_text]).tolist()
        results = self.collection.query(query_embeddings=query_vec, n_results=n_results)
        return results

    def delete_collection(self):
        """Deletes the entire collection (use with caution!)."""
        self.client.delete_collection(self.collection_name)

    def list_collections(self):
        """Returns a list of existing collections."""
        return [c.name for c in self.client.list_collections()]
