"""
Base model for all SQLAlchemy models.
Import all models here to ensure they are registered with Alembic.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
