"""Handler for processing SQS messages and triggering embedding generation."""

import json
from typing import Literal
from app.schemas.sqs_message import SqsMessageDto
from app.services.ai.embedding_service import EmbeddingService
from app.core.settings import settings


EventType = Literal["create", "update", "delete"]


class SqsMessageHandler:
    """Processes SQS messages and delegates to appropriate services.

    Handles workspace file events (create, update, delete) by managing
    embeddings in ChromaDB accordingly.
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
            # Parse and validate message
            data = json.loads(message_body)
            msg = SqsMessageDto(**data)

            print(
                f"[Handler] Processing event_type={msg.event_type}, "
                f"workspace={msg.workspace_id}, file={msg.file_id}, s3_key={msg.s3_key}"
            )

            # Route to appropriate handler based on event type
            if msg.event_type == "create":
                result = await self._handle_create_event(msg)
            elif msg.event_type == "update":
                result = await self._handle_update_event(msg)
            elif msg.event_type == "delete":
                result = await self._handle_delete_event(msg)
            else:
                raise ValueError(f"Unknown event type: {msg.event_type}")

            print(
                f"[Handler] Successfully processed event_type={msg.event_type}, file_id={msg.file_id}"
            )
            return result

        except json.JSONDecodeError as e:
            print(f"[Handler] Invalid JSON: {e}")
            raise ValueError(f"Invalid message format: {e}") from e
        except Exception as e:
            print(f"[Handler] Processing error: {e}")
            raise

    async def _handle_create_event(self, msg: SqsMessageDto) -> dict:
        """Handle file creation event by generating embeddings.

        Args:
            msg: Validated SQS message data.

        Returns:
            dict: Result with status and metadata.
        """
        print(f"[Handler] Creating embeddings for file_id={msg.file_id}")

        result = await self.embedding_service.add_workspace_file_embeddings(
            file_key=msg.s3_key,
            workspace_id=msg.workspace_id,
            file_id=str(msg.file_id),
            bucket=settings.aws_s3_workspace_bucket,
        )

        return {**result, "event_type": "create"}

    async def _handle_update_event(self, msg: SqsMessageDto) -> dict:
        """Handle file update event by deleting old embeddings and creating new ones.

        Args:
            msg: Validated SQS message data.

        Returns:
            dict: Result with status and metadata.
        """
        print(f"[Handler] Updating embeddings for file_id={msg.file_id}")

        # Step 1: Delete old embeddings
        delete_result = await self.embedding_service.delete_workspace_file_embeddings(
            workspace_id=msg.workspace_id,
            file_id=str(msg.file_id),
        )
        print(f"[Handler] Deleted {delete_result.get('count', 0)} old embeddings")

        # Step 2: Create new embeddings
        create_result = await self.embedding_service.add_workspace_file_embeddings(
            file_key=msg.s3_key,
            workspace_id=msg.workspace_id,
            file_id=str(msg.file_id),
            bucket=settings.aws_s3_workspace_bucket,
        )

        return {
            **create_result,
            "event_type": "update",
            "deleted_count": delete_result.get("count", 0),
        }

    async def _handle_delete_event(self, msg: SqsMessageDto) -> dict:
        """Handle file deletion event by removing all embeddings.

        Args:
            msg: Validated SQS message data.

        Returns:
            dict: Result with deletion status and count.
        """
        print(f"[Handler] Deleting embeddings for file_id={msg.file_id}")

        result = await self.embedding_service.delete_workspace_file_embeddings(
            workspace_id=msg.workspace_id,
            file_id=str(msg.file_id),
        )

        return {**result, "event_type": "delete"}
