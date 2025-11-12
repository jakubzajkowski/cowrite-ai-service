"""Handler for processing SQS messages and triggering embedding generation."""

import json
from app.schemas.sqs_message import SqsMessageDto
from app.services.ai.embedding_service import EmbeddingService


class SqsMessageHandler:
    """Processes SQS messages and delegates to appropriate services.

    Handles workspace file upload messages by extracting text,
    generating embeddings, and storing them in ChromaDB.
    """

    def __init__(self, embedding_service: EmbeddingService):
        """Initialize the SQS message handler.

        Args:
            embedding_service: Service for generating and storing embeddings.
        """
        self.embedding_service = embedding_service

    async def handle_workspace_file_message(self, message_body: str) -> dict:
        """Process a workspace file message from SQS.

        Args:
            message_body: JSON string containing SqsMessageDto data.

        Returns:
            dict: Processing result with status and metadata.

        Raises:
            ValueError: If message parsing or validation fails.
            Exception: If embedding generation fails.
        """
        try:
            data = json.loads(message_body)
            msg = SqsMessageDto(**data)

            print(
                f"[Handler] Processing workspace={msg.workspace_id}, "
                f"file={msg.file_id}, s3_key={msg.s3_key}"
            )

            result = await self.embedding_service.add_workspace_file_embeddings(
                file_key=msg.s3_key,
                workspace_id=msg.workspace_id,
                file_id=str(msg.file_id),
                bucket="my-notes-bucket",
            )

            print(f"[Handler] Successfully processed file_id={msg.file_id}")
            return result

        except json.JSONDecodeError as e:
            print(f"[Handler] Invalid JSON: {e}")
            raise ValueError(f"Invalid message format: {e}") from e
        except Exception as e:
            print(f"[Handler] Processing error: {e}")
            raise
