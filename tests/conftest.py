"""Test fixtures: FastAPI app with Testcontainers for Postgres and ChromaDB.

Provides a configured FastAPI application with temporary databases
and an async HTTP client for integration tests.
"""

import asyncio
from contextlib import ExitStack
from typing import AsyncGenerator
import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.chroma import ChromaContainer
import chromadb

from app.main import create_app
from app.db.base import Base
from app.db.database import get_db as app_get_db


@pytest.fixture(scope="session")
def fastapi_app():
    """FastAPI app z Postgres i Chroma testcontainers."""
    with ExitStack() as stack:
        chroma = stack.enter_context(ChromaContainer())
        chroma_host = chroma.get_container_host_ip()
        chroma_port = int(chroma.get_exposed_port(8000))

        chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        collection = chroma_client.get_or_create_collection("test")
        print("Chroma collection:", collection.name)

        pg = stack.enter_context(PostgresContainer("postgres:16-alpine"))
        sync_url = pg.get_connection_url()
        async_url = sync_url.replace("+psycopg2", "+asyncpg")

        sync_engine = create_engine(sync_url)
        Base.metadata.create_all(bind=sync_engine)

        async_engine = create_async_engine(async_url, echo=False)
        async_session_factory = sessionmaker(
            async_engine, class_=AsyncSession, expire_on_commit=False
        )

        async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
            async with async_session_factory() as session:
                yield session

        application = create_app()
        application.dependency_overrides[app_get_db] = override_get_db

        yield application

        application.dependency_overrides.pop(app_get_db, None)
        Base.metadata.drop_all(bind=sync_engine)
        sync_engine.dispose()
        asyncio.run(async_engine.dispose())


@pytest.fixture()
async def client(
    fastapi_app,  # pylint: disable=redefined-outer-name
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async HTTP client bound to the FastAPI application."""
    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
