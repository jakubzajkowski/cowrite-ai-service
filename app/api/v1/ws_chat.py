"""
WebSocket endpoint for handling chat messages with Gemini AI using ChatService.
"""

from http.cookies import SimpleCookie
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.chat.chat_service import ChatService
from app.services.ai.embedding_service import EmbeddingService
from app.services.files.s3_service import S3Client
from app.services.ai.file_context_service import FileContextService
from app.services.files.text_extraction_service import TextExtractionService
from app.services.auth.auth_service import verify_user
from app.core.settings import settings
from app.services.ai.chroma_client import ChromaClient
from app.services.ai.gemini_text_service import GeminiTextService

router = APIRouter()


async def get_chroma_client() -> ChromaClient:
    """Factory for Chroma client."""
    return ChromaClient()


async def get_s3_client() -> S3Client:
    """Factory for S3 client."""
    return S3Client()


async def get_text_extraction_service() -> TextExtractionService:
    """Factory for TextExtractionService."""
    return TextExtractionService()


async def get_embedding_service(
    s3_client: S3Client = Depends(get_s3_client),
    chroma_client: ChromaClient = Depends(get_chroma_client),
    text_extraction_service: TextExtractionService = Depends(
        get_text_extraction_service
    ),
) -> EmbeddingService:
    """Factory for EmbeddingService."""
    return EmbeddingService(chroma_client, s3_client, text_extraction_service)


async def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Provide ChatService."""
    return ChatService(db)


async def get_file_context_service(
    db: AsyncSession = Depends(get_db),
) -> FileContextService:
    """Provide FileContextService using cached EmbeddingService."""
    return FileContextService(embedding_service=Depends(get_embedding_service), db=db)


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

            # 🧠 Zapisz wiadomość użytkownika w DB
            message = await chat_service.create_message(
                conversation_id=conversation_id,
                prompt=prompt,
                user_id=user["id"],
            )

            # 🤖 Wygeneruj odpowiedź z Gemini + kontekst z plików
            response = await gemini_text_service.generate(
                conversation_id=conversation_id,
                user_id=user["id"],
                user_prompt=prompt,
            )

            # 💾 Zaktualizuj wiadomość w DB z odpowiedzią AI
            await chat_service.update_message_response(
                message_id=message.id,
                response=response,
                status="completed",
            )

            await websocket.send_text(response)

    except WebSocketDisconnect:
        print(f"User {user['id']} disconnected")
