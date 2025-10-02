from fastapi import FastAPI
from app.api.v1.test import router as users_router

app = FastAPI(title="Example FastAPI App")

app.include_router(users_router, prefix="/api/v1/users", tags=["users"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
