from pydantic import BaseModel
from typing import Optional


class ConversationRequest(BaseModel):
    title: Optional[str]
