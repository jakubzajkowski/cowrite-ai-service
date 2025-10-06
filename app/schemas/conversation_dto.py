from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ConversationDTO(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
