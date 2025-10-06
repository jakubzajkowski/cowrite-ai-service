"""Application entrypoint defining the FastAPI instance and root endpoints.

Exposes:
    app (FastAPI): The FastAPI application object used by ASGI servers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.test import router as users_router
from app.api.v1.chat import router as chat_router

app = FastAPI(title="Example FastAPI App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])


@app.get("/health")
async def health_check():
    """Return a simple health status payload for uptime probes."""
    return {"status": "ok"}
