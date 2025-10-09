"""Application entrypoint defining the FastAPI instance and root endpoints.

Exposes:
    app (FastAPI): The FastAPI application object used by ASGI servers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.test import router as users_router
from app.api.v1.chat import router as chat_router
from app.api.v1.ws_chat import router as ws_chat_router
from prometheus_fastapi_instrumentator import Instrumentator


def create_app() -> FastAPI:
    """Create and configure FastAPI app instance."""
    _app = FastAPI(title="Example FastAPI App")

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Instrumentator().instrument(_app).expose(_app)

    _app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
    _app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
    _app.include_router(ws_chat_router, tags=["websocket"])

    @_app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return _app


app = create_app()  # pylint redefines-outer-name
