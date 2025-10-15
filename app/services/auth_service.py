"""Service for user authentication and verification."""

import httpx
from app.core.settings import settings


async def verify_user(token: str) -> dict | None:
    """
    Verify the user token by calling the user service.
    Args:
        token (str): The user token to verify.
    Returns user data if the token is valid, otherwise None.
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{settings.user_service_url}/me",
                cookies={settings.user_cookie_name: token},
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except httpx.RequestError:
            return None
