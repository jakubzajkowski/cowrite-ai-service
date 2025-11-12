"""Service to generate text using the Gemini API with context from external files."""

from app.services.ai.file_context_service import FileContextService
from app.services.ai.gemini_client import GeminiClient
from app.services.ai.workspace_context_service import WorkspaceContextService
from prompts.assistant_prompt_v1 import MARKDOWN_ASSISTANT_PROMPT_V2
from prompts.prompt_composer import PromptComposer


class GeminiTextService:
    """Coordinates prompt building and Gemini API calls."""

    def __init__(
        self,
        file_context_service: FileContextService,
        workspace_context_service: WorkspaceContextService,
    ):
        self.file_context_service = file_context_service
        self.workspace_context_service = workspace_context_service
        self.client = GeminiClient()

    async def generate(self, conversation_id: int, user_id: int, user_prompt: str):
        """
        Generate text from Gemini API using user prompt and semantic context
        from conversation files stored in ChromaDB.
        """
        file_context = await self.file_context_service.get_external_file_context(
            conversation_id=conversation_id,
            user_id=user_id,
            query_text=user_prompt,
            max_files=3,
            max_tokens=8000,
            top_k=3,
        )
        workspace_context = (
            await self.workspace_context_service.get_workspace_file_context(
                workspace_id=user_id,
                query_text=user_prompt,
                n_results=3,
                max_tokens=10000,
            )
        )

        full_prompt = PromptComposer.compose(
            user_prompt=user_prompt,
            file_context=file_context,
            system_instruction=MARKDOWN_ASSISTANT_PROMPT_V2,
            workspace_context=workspace_context,
        )

        print("=== Sending to Gemini ===")
        print(full_prompt)
        print("==========================")

        response = await self.client.generate(full_prompt)

        return response
