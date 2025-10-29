"""Test fixtures: provide a FastAPI application backed by a Testcontainers Postgres
and an async HTTP client for tests.

Fixtures are intentionally minimal to keep tests fast and readable.
"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.main import create_app
from app.db.base import Base
from app.db.database import get_db as app_get_db


@pytest.fixture(scope="session")
def fastapi_app():
    """Create a FastAPI app configured to use a temporary Postgres database.

    The fixture starts a Postgres container, creates tables synchronously,
    sets up an async session factory, and overrides the app's `get_db` dependency.
    """
    with PostgresContainer("postgres:16-alpine") as pg:
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
    fastapi_app,
) -> AsyncGenerator[httpx.AsyncClient, None]:  # pylint: disable=redefined-outer-name
    """Provide an async HTTP client bound to the FastAPI application."""
    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
