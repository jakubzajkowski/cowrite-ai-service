"""Test fixtures for unit tests with mocked dependencies.

Provides mocked FastAPI app, database sessions, and AI services
without requiring real containers or heavy ML models.
"""

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import create_app
from app.db.database import get_db


@pytest.fixture
def mock_embedding_model():
    """Mock SentenceTransformer to avoid loading real model."""
    mock_model = MagicMock()
    mock_model.encode.return_value = [[0.1] * 768]  # Fake embedding vector
    return mock_model


@pytest.fixture
def mock_chroma_client():
    """Mock ChromaDB client for vector search."""
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = MagicMock()
    mock_client.search.return_value = []
    return mock_client


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for file operations."""
    mock_client = AsyncMock()
    mock_client.upload_file.return_value = "s3://bucket/file.pdf"
    mock_client.download_file.return_value = b"fake file content"
    return mock_client


@pytest.fixture
def mock_text_extractor():
    """Mock TextExtractionService for document parsing."""
    mock_extractor = MagicMock()
    mock_extractor.extract_text.return_value = "Extracted text from document"
    return mock_extractor


@pytest.fixture
def mock_db_session():
    """Mock AsyncSession for database operations."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def fastapi_app(  # pylint: disable=redefined-outer-name
    mock_embedding_model,  # pylint: disable=redefined-outer-name
    mock_chroma_client,  # pylint: disable=redefined-outer-name
    mock_s3_client,  # pylint: disable=redefined-outer-name
    mock_text_extractor,  # pylint: disable=redefined-outer-name
    mock_db_session,  # pylint: disable=redefined-outer-name
):
    """Create FastAPI app with mocked heavy dependencies."""
    with patch("app.main.SentenceTransformer", return_value=mock_embedding_model):
        application = create_app()

        # Override app.state with mocks
        application.state.embedding_model = mock_embedding_model
        application.state.chroma_client = mock_chroma_client
        application.state.s3_client = mock_s3_client
        application.state.text_extractor_service = mock_text_extractor

        # Mock database dependency
        async def override_get_db():
            yield mock_db_session

        application.dependency_overrides[get_db] = override_get_db

        yield application

        # Clean up
        application.dependency_overrides.clear()


@pytest.fixture
async def client(  # pylint: disable=redefined-outer-name
    fastapi_app: FastAPI,  # pylint: disable=redefined-outer-name
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async HTTP client bound to the mocked FastAPI application."""
    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
