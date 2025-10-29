from sqlalchemy import BigInteger, Column, Integer, String, TIMESTAMP, func
from app.db.base import Base
from sqlalchemy.orm import relationship


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    files = relationship(
        "ChatFile", back_populates="conversation", cascade="all, delete-orphan"
    )
