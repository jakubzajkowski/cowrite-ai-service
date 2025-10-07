"""WebSocket endpoint for handling chat messages with Gemini AI."""

from http.cookies import SimpleCookie

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.db.database import async_session
from app.services.auth_service import verify_user
from app.services.chat_service import create_message, update_message_response
from app.services.gemini_service import gemini_service

router = APIRouter()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: int):
    """WebSocket handler for chat messages in a given conversation."""
    await websocket.accept()

    cookie_header = websocket.headers.get("cookie")
    cookies = SimpleCookie(cookie_header)
    token = cookies.get("COWRITE_SESSION_ID")
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

    async with async_session() as db:
        try:
            while True:
                prompt = await websocket.receive_text()

                message = await create_message(
                    db=db,
                    conversation_id=conversation_id,
                    prompt=prompt,
                    user_id=user["id"],
                )

                response = await gemini_service.generate_text_async(prompt=prompt)

                await update_message_response(
                    db=db,
                    message_id=message.id,
                    response=response,
                    status="completed",
                )

                await websocket.send_text(response)

        except WebSocketDisconnect:
            print(f"User {user['id']} disconnected")
