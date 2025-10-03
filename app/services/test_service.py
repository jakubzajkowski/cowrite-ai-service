"""Simple in-memory user service used for early development & tests.

This module provides a temporary implementation that mimics a data layer
using a process-local Python list. It will be replaced by a persistent
repository/database backed implementation in production.
"""

from typing import List, Dict, Optional

USERS_DB: List[Dict[str, object]] = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]


def list_users() -> List[Dict[str, object]]:
    """Return the list of all users."""
    return USERS_DB


def get_user(user_id: int) -> Optional[Dict[str, object]]:
    """Return a user matching ``user_id`` or None if absent.

    Args:
        user_id: The numeric identifier of the user.
    """
    for user in USERS_DB:
        if user["id"] == user_id:
            return user
    return None


def create_user(name: str) -> Dict[str, object]:
    """Create and persist a new user with the next incremental id.

    Args:
        name: The display name of the user.
    """
    new_id = max(user["id"] for user in USERS_DB) + 1 if USERS_DB else 1
    new_user: Dict[str, object] = {"id": new_id, "name": name}
    USERS_DB.append(new_user)
    return new_user
