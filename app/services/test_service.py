from typing import List, Dict

# tymczasowa "baza" w pamięci
USERS_DB = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

def list_users() -> List[Dict]:
    return USERS_DB

def get_user(user_id: int) -> Dict | None:
    for user in USERS_DB:
        if user["id"] == user_id:
            return user
    return None

def create_user(name: str) -> Dict:
    new_id = max(user["id"] for user in USERS_DB) + 1
    new_user = {"id": new_id, "name": name}
    USERS_DB.append(new_user)
    return new_user
