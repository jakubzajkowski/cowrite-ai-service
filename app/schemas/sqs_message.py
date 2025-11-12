"""Schema for SQS message parsing."""

from pydantic import BaseModel, Field


class SqsMessageDto(BaseModel):
    """Data transfer object for SQS workspace file messages.

    Attributes:
        workspace_id: Unique identifier of the workspace.
        file_id: Unique identifier of the file.
        s3_key: S3 object key for file location.
    """

    workspace_id: int = Field(..., alias="workspaceId")
    file_id: int = Field(..., alias="fileId")
    s3_key: str = Field(..., alias="s3Key")
