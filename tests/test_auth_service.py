"""Unit tests for auth_service.verify_user."""

import json
import time
import jwt
import pytest

from app.core.settings import settings
from app.services.auth.auth_service import verify_user


@pytest.mark.asyncio
async def test_verify_user_valid_token_returns_user_dict():
    """verify_user returns the decoded user dict for a valid token."""
    user = {"id": 123, "email": "user@example.com"}
    payload = {"sub": json.dumps(user), "exp": int(time.time()) + 60}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")

    result = await verify_user(token)

    assert result == user


@pytest.mark.asyncio
async def test_verify_user_invalid_token_returns_none():
    """verify_user returns None for a token signed with the wrong secret."""
    user = {"id": 1}
    payload = {"sub": json.dumps(user), "exp": int(time.time()) + 60}
    wrong_secret = "not_the_right_secret"
    token = jwt.encode(payload, wrong_secret, algorithm="HS256")

    result = await verify_user(token)

    assert result is None


@pytest.mark.asyncio
async def test_verify_user_expired_token_returns_none():
    """verify_user returns None for an expired token."""
    user = {"id": 2}
    payload = {"sub": json.dumps(user), "exp": int(time.time()) - 10}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")

    result = await verify_user(token)

    assert result is None
