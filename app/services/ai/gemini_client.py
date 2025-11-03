"""Gemini service for generating text using Google Gemini API.

This module provides a GeminiClient class that can generate text based on a given prompt.
It reads the API key from the application's settings and interfaces with the Google GenAI SDK.
"""

import asyncio
from google import genai
from google.genai import types

from app.core.settings import settings
from prompts.assistant_prompt_v1 import MARKDOWN_ASSISTANT_PROMPT_V1


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize the GeminiClient with API key from settings."""
        self.api_key = settings.gemini_api_key
        self.default_model = "gemini-2.5-flash"
        self.client = genai.Client(api_key=self.api_key)

    async def generate(self, prompt: str, model: str | None = None) -> str:
        """Generate text asynchronously using Gemini API."""
        model = model or self.default_model

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=model,
                config=types.GenerateContentConfig(
                    system_instruction=MARKDOWN_ASSISTANT_PROMPT_V1
                ),
                contents=prompt,
            ),
        )

        return getattr(response, "text", "")
