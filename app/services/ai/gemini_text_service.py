"""Service to generate text using the Gemini API with context from external files."""

import asyncio
from app.services.ai.file_context_service import FileContextService
from app.services.ai.gemini_service import GeminiClient
from prompts.assistant_prompt_v1 import MARKDOWN_ASSISTANT_PROMPT_V1
from prompts.prompt_composer import PromptComposer


class GeminiTextService:
    """Coordinates prompt building and Gemini API calls."""

    def __init__(self, file_context_service: FileContextService):
        self.file_context_service = file_context_service
        self.client = GeminiClient()

    """Generate text using Gemini with context from external files."""

    async def generate(self, conversation_id: int, user_prompt: str):
        file_context = await self.file_context_service.get_external_file_context(
            conversation_id
        )
        full_prompt = PromptComposer.compose(
            user_prompt=user_prompt,
            file_context=file_context,
            system_instruction=MARKDOWN_ASSISTANT_PROMPT_V1,
        )

        print("=== Sending to Gemini ===")
        print(full_prompt[:1000])
        print("==========================")

        response = await asyncio.to_thread(self.client.generate, full_prompt)
        return response
