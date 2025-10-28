"""Service for user authentication and verification."""

import json
import jwt
from app.core.settings import settings


async def verify_user(token: str) -> dict | None:
    """
    Verify the user token by calling the user service.
    Args:
        token (str): The user token to verify.
    Returns user data if the token is valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        user_data = json.loads(payload["sub"])
        return user_data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
