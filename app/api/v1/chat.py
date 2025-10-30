"""
Chat API endpoints using class-based ChatService.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.chat_service import ChatService
from app.schemas.conversation_request import ConversationRequest
from app.schemas.conversation_dto import ConversationDTO

router = APIRouter()


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """
    Provide an instance of ChatService with a DB session.
    """
    return ChatService(db)


@router.post("/conversations", response_model=ConversationDTO)
async def http_create_conversation(
    request: Request,
    data: ConversationRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Create a new conversation.
    """
    user = request.state.user if request.state.user else None

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conversation = await chat_service.create_conversation(
            user_id=user["id"], title=data.title
        )
        return conversation
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.get("/conversations", response_model=List[ConversationDTO])
async def http_get_conversations(
    request: Request,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Get all conversations for a user.
    """
    user = request.state.user if request.state.user else None

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        conversations = await chat_service.get_conversations_by_user(user_id=user["id"])
        return conversations
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
