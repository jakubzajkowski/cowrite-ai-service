"""
WebSocket endpoint for handling chat messages with Gemini AI using ChatService.
"""

from http.cookies import SimpleCookie

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.chat_service import ChatService
from app.services.gemini_service import GeminiClient
from app.services.auth_service import verify_user
from app.core.settings import settings

router = APIRouter()


async def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Provide an instance of ChatService with a DB session."""
    return ChatService(db)


def get_gemini_service() -> GeminiClient:
    """Provide an instance of GeminiClient."""
    return GeminiClient()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
    chat_service: ChatService = Depends(get_chat_service),
    gemini_service: GeminiClient = Depends(get_gemini_service),
):
    """WebSocket handler for chat messages in a given conversation."""
    await websocket.accept()

    cookie_header = websocket.headers.get("cookie")
    cookies = SimpleCookie(cookie_header)
    token = cookies.get(settings.user_cookie_name)
    token_value = token.value if token else None

    if not token_value:
        await websocket.send_text("Missing session cookie")
        await websocket.close()
        return

    user = await verify_user(token_value)
    if not user:
        await websocket.send_text("Invalid session")
        await websocket.close()
        return

    try:
        while True:
            prompt = await websocket.receive_text()

            message = await chat_service.create_message(
                conversation_id=conversation_id,
                prompt=prompt,
                user_id=user["id"],
            )

            response = await gemini_service.generate_text_async(prompt=prompt)

            await chat_service.update_message_response(
                message_id=message.id,
                response=response,
                status="completed",
            )

            await websocket.send_text(response)

    except WebSocketDisconnect:
        print(f"User {user['id']} disconnected")
