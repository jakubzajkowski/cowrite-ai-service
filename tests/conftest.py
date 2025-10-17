# pylint: disable=wrong-import-position, redefined-outer-name, unused-argument
"""Configurations for pytest with FastAPI + async SQLAlchemy + Testcontainers."""

import asyncio
import sys
import os
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import create_app
from app.db.base import Base
from app.db.database import get_db


@pytest.fixture(scope="session")
def event_loop():
    """Let pytest use an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    """Runs a Postgres container for the duration of the test session."""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@pytest.fixture(scope="session")
async def async_engine(postgres_container):
    """Creates async engine for the test database."""
    db_url = postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(db_url, echo=False, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture()
async def async_db_session(async_engine):
    """Provides a new database session for a test."""
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


@pytest.fixture()
def client(async_db_session):
    """Provides a TestClient with overridden database dependency."""
    app = create_app()

    def override_get_db():
        yield async_db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
