from fastapi import APIRouter, HTTPException
from app.services.test_service import list_users, get_user, create_user

router = APIRouter()

@router.get("/")
async def get_users():
    return list_users()

@router.get("/{user_id}")
async def get_user_endpoint(user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/")
async def create_user_endpoint(user: dict):
    name = user.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    return create_user(name)