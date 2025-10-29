"""
Database session management.
"""

import ssl
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings


connect_args = {}
if "azure.com" in settings.database_url:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connect_args = {
        "ssl": ssl_context,
    }

engine = create_async_engine(
    settings.database_url, echo=False, connect_args=connect_args
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """
    Get a database session.
    """
    async with async_session() as session:
        yield session
