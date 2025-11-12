"""Asynchronous client for polling and processing AWS SQS messages."""

import asyncio
import aioboto3
from app.core.settings import settings
from app.services.files.sqs_message_handler import SqsMessageHandler


class SQSClient:
    """Manages background polling of SQS queue and message processing."""

    def __init__(self, message_handler: SqsMessageHandler):
        """Initialize SQS client with configuration and handler.

        Args:
            message_handler: Handler for processing received messages.
        """
        self.queue_url = settings.sqs_workspace_queue_url
        self.region_name = settings.aws_region
        self._stop_event = asyncio.Event()
        self._task = None
        self.message_handler = message_handler

    async def start(self):
        """Start background polling task."""
        if not self._task:
            self._task = asyncio.create_task(self._poll_sqs())
            print("[SQS] Polling started.")

    async def stop(self):
        """Stop background polling gracefully."""
        if self._task:
            print("[SQS] Stopping...")
            self._stop_event.set()
            await self._task
            print("[SQS] Stopped.")
            self._task = None

    async def _poll_sqs(self):
        """Worker: continuously receive and process messages from SQS."""
        session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=self.region_name,
        )
        async with session.client(
            "sqs", endpoint_url="http://localhost:4566", region_name=self.region_name
        ) as sqs:
            while not self._stop_event.is_set():
                try:
                    response = await sqs.receive_message(
                        QueueUrl=self.queue_url,
                        MaxNumberOfMessages=10,
                        WaitTimeSeconds=10,
                    )
                    messages = response.get("Messages", [])
                    for msg in messages:
                        await self._handle_message(msg, sqs)
                except Exception as e:
                    print(f"[SQS] Error: {e}")

                await asyncio.sleep(1)

    async def _handle_message(self, msg: dict, sqs):
        """Process a single SQS message and delegate to handler.

        Args:
            msg: Raw SQS message dictionary.
            sqs: Active SQS client for message deletion.
        """
        body = msg["Body"]
        print(f"[SQS] Received message: {body}")

        try:
            result = await self.message_handler.handle_workspace_file_message(body)
            print(f"[SQS] Processing result: {result}")

            await sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=msg["ReceiptHandle"],
            )
            print("[SQS] Message deleted.")

        except Exception as e:
            print(f"[SQS] Failed to process message: {e}")
