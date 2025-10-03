"""User API endpoints (temporary example implementation).

Routers here provide CRUD-like operations for an in‑memory users list.
This is intentionally simple and will be replaced with database backed
logic later.
"""

from fastapi import APIRouter, HTTPException
from app.services.test_service import list_users, get_user, create_user

router = APIRouter()


@router.get("/")
async def get_users():
    """Return all users currently stored in memory."""
    return list_users()


@router.get("/{user_id}")
async def get_user_endpoint(user_id: int):
    """Return a single user by id or raise 404 if absent.

    Args:
        user_id: Numeric identifier of the user.
    """
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/")
async def create_user_endpoint(user: dict):
    """Create a new user given a JSON body with a 'name' field."""
    name = user.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    return create_user(name)
