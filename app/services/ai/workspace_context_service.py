"""Service to extract and compile context from workspace files stored in ChromaDB."""

from app.services.ai.embedding_service import EmbeddingService


class WorkspaceContextService:
    """Service to compile context from embeddings of all files in a workspace."""

    def __init__(self, embedding_service: EmbeddingService):
        """Initialize the workspace context service.

        Args:
            embedding_service: Service for querying embeddings from ChromaDB.
        """
        self.embedding_service = embedding_service

    async def get_workspace_file_context(
        self,
        workspace_id: int,
        query_text: str,
        n_results: int = 3,
        max_tokens: int = 10000,
    ) -> str:
        """Retrieve relevant semantic context from all workspace files.

        Queries ChromaDB for the most relevant text chunks across all files
        in the specified workspace based on semantic similarity.

        Args:
            workspace_id: Workspace identifier.
            query_text: Query string for semantic search.
            n_results: Number of top results to return per query (default: 3).
            max_tokens: Maximum character length of returned context (default: 10000).

        Returns:
            str: Formatted context string with relevant file excerpts,
            or empty string if no results.
        """
        result = await self.embedding_service.query_workspace_context(
            workspace_id=workspace_id,
            query_text=query_text,
            n_results=n_results,
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]

        if not documents:
            print(
                f"[WorkspaceContext] No results found for workspace_id={workspace_id}"
            )
            return ""

        print(
            f"[WorkspaceContext] Found {len(documents)} for workspace_id={workspace_id}"
        )

        file_groups = {}
        for doc, meta in zip(documents, metadatas):
            file_name = meta.get("file_name", "Unknown")
            if file_name not in file_groups:
                file_groups[file_name] = []
            file_groups[file_name].append(doc)

        context_parts = []
        for file_name, docs in file_groups.items():
            file_context = f"📄 File: {file_name}\n" + "\n---\n".join(docs)
            context_parts.append(file_context)

        context = "\n\n===========================\n\n".join(context_parts)

        if len(context) > max_tokens:
            context = context[:max_tokens] + "\n\n[... context truncated ...]"

        return context
