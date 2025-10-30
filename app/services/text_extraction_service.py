"""Service for extracting text from uploaded files."""

import io
import logging
from typing import Optional

from pypdf import PdfReader
from docx import Document

logger = logging.getLogger(__name__)


class TextExtractionService:
    """
    Service for extracting text from uploaded files.
    Supports PDF, DOCX, TXT, and Markdown (.md) formats.
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

    async def extract_text(self, filename: str, content: bytes) -> Optional[str]:
        """
        Main method: detects file type and extracts text.
        Returns None if the format is unsupported or extraction fails.
        """
        filename_lower = filename.lower()
        text = None

        try:
            if filename_lower.endswith(".pdf"):
                text = self._extract_from_pdf(content)
            elif filename_lower.endswith(".docx"):
                text = self._extract_from_docx(content)
            elif filename_lower.endswith(".txt") or filename_lower.endswith(".md"):
                text = self._extract_from_txt_or_md(content)
            else:
                logger.warning("Unsupported file type: %s", filename)
                return None

        # pylint: disable=broad-exception-caught
        except Exception as e:
            logger.exception("Error extracting text from %s: %s", filename, e)
            return None

        return text.strip() if text else None

    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from a PDF file (bytes)."""
        reader = PdfReader(io.BytesIO(content))
        text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
        return "\n".join(text)

    def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from a DOCX file (bytes)."""
        document = Document(io.BytesIO(content))
        paragraphs = [p.text for p in document.paragraphs]
        return "\n".join(paragraphs)

    def _extract_from_txt_or_md(self, content: bytes) -> str:
        """
        Extract text from TXT or Markdown (.md) files, preserving formatting.
        """
        text = content.decode("utf-8", errors="ignore")
        lines = [line.rstrip() for line in text.splitlines()]
        return "\n".join(lines)
