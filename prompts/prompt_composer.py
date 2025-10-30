"""Module for composing prompts for LLMs."""

from typing import Optional

class PromptComposer:
    """Builds the final prompt sent to the LLM."""

    @staticmethod
    def compose(
        user_prompt: str,
        file_context: Optional[str] = None,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Combine system prompt, file context, and user input into a single formatted prompt."""
        sections = []

        if system_instruction:
            sections.append(f"### System Instruction\n{system_instruction.strip()}")

        if file_context:
            sections.append(f"### File Context\n{file_context.strip()}")

        sections.append(f"### User Prompt\n{user_prompt.strip()}")

        return "\n\n".join(sections)