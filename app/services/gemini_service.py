"""Gemini service for generating text using Google Gemini API.

This module provides a GeminiClient class that can generate text based on a given prompt.
It reads the API key from the application's settings and interfaces with the Google GenAI SDK.
"""

import asyncio
from google import genai
from google.genai import types

from app.core.settings import settings


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize the GeminiClient with API key from settings."""
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key)

    def generate_text(self, prompt: str, model: str = "gemini-2.5-flash"):
        """
        Generate text using the specified Gemini model.

        Args:
            prompt (str): The text prompt to generate content from.
            model (str, optional): The Gemini model to use. Defaults to "gemini-2.5-flash".

        Returns:
            response: The response object from the Gemini API containing generated text.
        """
        response = self.client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction="You are a cat. Your name is Neko."
            ),
            contents=prompt,
        )
        return response

    async def generate_text_async(self, prompt: str, model: str = "gemini-2.5-flash"):
        """
        Async wrapper for generate_text – runs in a thread to avoid blocking event loop.
        Args:
            prompt (str): The text prompt to generate content from.
            model (str, optional): The Gemini model to use. Defaults to "gemini-2.5-flash".

        Returns:
            response: The response object from the Gemini API containing generated text.
        """
        response = await asyncio.to_thread(self.generate_text, prompt, model)
        return response.text


gemini_service = GeminiClient()
