"""
Chat API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.chat_service import (
    create_conversation,
    get_conversations_by_user,
)
from app.schemas.conversation_request import ConversationRequest
from app.schemas.conversation_dto import ConversationDTO

router = APIRouter()


# -------------------------
# Conversation endpoints
# -------------------------
@router.post("/conversations", response_model=ConversationDTO)
async def http_create_conversation(
    data: ConversationRequest,
    cowrite_session_id: str | None = Cookie(default=None, alias="COWRITE_SESSION_ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new conversation.
    """
    if not cowrite_session_id:
        raise HTTPException(status_code=401, detail="Missing session cookie")
    try:
        conversation = await create_conversation(db, cowrite_session_id, data.title)
        return conversation
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.get("/conversations", response_model=List[ConversationDTO])
async def http_get_conversations(
    cowrite_session_id: str | None = Cookie(default=None, alias="COWRITE_SESSION_ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all conversations for a user.
    """
    if not cowrite_session_id:
        raise HTTPException(status_code=401, detail="Missing session cookie")
    try:
        conversations = await get_conversations_by_user(db, cowrite_session_id)
        return conversations
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
