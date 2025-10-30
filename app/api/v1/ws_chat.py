"""
WebSocket endpoint for handling chat messages with Gemini AI using ChatService.
"""

from http.cookies import SimpleCookie

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.chat.chat_service import ChatService
from app.services.ai.file_context_service import FileContextService
from app.services.auth.auth_service import verify_user
from app.core.settings import settings
from app.services.files.s3_service import S3Client
from app.services.files.text_extraction_service import TextExtractionService
from app.services.ai.gemini_text_service import GeminiTextService

router = APIRouter()


async def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Provide ChatService."""
    return ChatService(db)


async def get_file_context_service(
    db: AsyncSession = Depends(get_db),
) -> FileContextService:
    """Provide FileContextService."""
    text_extractor = TextExtractionService()
    s3_client = S3Client()
    return FileContextService(text_extractor=text_extractor, s3_client=s3_client, db=db)


async def get_gemini_text_service(
    file_context_service: FileContextService = Depends(get_file_context_service),
) -> GeminiTextService:
    """Provide GeminiTextService with dependencies."""
    return GeminiTextService(file_context_service=file_context_service)


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
    chat_service: ChatService = Depends(get_chat_service),
    gemini_text_service: GeminiTextService = Depends(get_gemini_text_service),
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

            response = await gemini_text_service.generate(conversation_id, prompt)

            await chat_service.update_message_response(
                message_id=message.id,
                response=response.text,
                status="completed",
            )

            await websocket.send_text(response.text)

    except WebSocketDisconnect:
        print(f"User {user['id']} disconnected")
