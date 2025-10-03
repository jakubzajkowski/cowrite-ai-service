"""Application entrypoint defining the FastAPI instance and root endpoints.

Exposes:
    app (FastAPI): The FastAPI application object used by ASGI servers.
"""

from fastapi import FastAPI
from app.api.v1.test import router as users_router

app = FastAPI(title="Example FastAPI App")

app.include_router(users_router, prefix="/api/v1/users", tags=["users"])


@app.get("/health")
async def health_check():
    """Return a simple health status payload for uptime probes."""
    return {"status": "ok"}
