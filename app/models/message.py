from sqlalchemy import BigInteger, Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    partial_response = Column(Text, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
