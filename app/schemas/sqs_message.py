"""Schema for SQS message parsing."""

from typing import Literal
from pydantic import BaseModel, Field


EventType = Literal["create", "update", "delete"]


class SqsMessageDto(BaseModel):
    """Data transfer object for SQS workspace file messages.

    Attributes:
        workspace_id: Unique identifier of the workspace.
        file_id: Unique identifier of the file.
        s3_key: S3 object key for file location.
        event_type: Type of event ('create', 'update', or 'delete').
    """

    workspace_id: int = Field(..., alias="workspaceId")
    file_id: int = Field(..., alias="fileId")
    s3_key: str = Field(..., alias="s3Key")
    event_type: EventType = Field(..., alias="eventType")
