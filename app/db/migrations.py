"""
Migration utilities for database management.
"""

from sqlalchemy import create_engine
from app.db.base import Base
from app.core.settings import settings


def get_sync_database_url() -> str:
    """
    Convert async database URL to sync URL for migrations.
    """
    database_url = settings.database_url

    if database_url.startswith("sqlite+aiosqlite"):
        return database_url.replace("sqlite+aiosqlite", "sqlite")
    if database_url.startswith("postgresql+asyncpg"):
        return database_url.replace("postgresql+asyncpg", "postgresql")

    return database_url


def create_tables():
    """
    Create all tables (for development only - use alembic for production).
    This is useful for quick setup without running migrations.
    """
    sync_url = get_sync_database_url()
    engine = create_engine(sync_url)
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")


if __name__ == "__main__":
    create_tables()
