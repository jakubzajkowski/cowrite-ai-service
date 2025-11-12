"""
Application entrypoint defining the FastAPI instance and root endpoints.

Exposes:
    app (FastAPI): The FastAPI application object used by ASGI servers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sentence_transformers import SentenceTransformer
from app.api.v1.chat import router as chat_router
from app.api.v1.ws_chat import router as ws_chat_router
from app.api.v1.upload import router as upload_router

from app.middleware.auth_middleware import AuthMiddleware
from app.services.ai.chroma_client import ChromaClient
from app.services.ai.embedding_service import EmbeddingService
from app.services.files.s3_service import S3Client
from app.services.files.sqs_client import SQSClient
from app.services.files.sqs_message_handler import SqsMessageHandler
from app.services.files.text_extraction_service import TextExtractionService


@asynccontextmanager
async def lifespan(_app: FastAPI):  # pylint redefines-outer-name
    """
    FastAPI lifespan context manager.
    Preload heavy resources like embedding models and clients.
    """
    print("📥 Loading embedding model…")
    embedding_model = SentenceTransformer("intfloat/multilingual-e5-base")
    print("✅ Model loaded successfully.")

    chroma_client = ChromaClient(model=embedding_model)
    s3_client = S3Client()
    text_extractor_service = TextExtractionService()

    embedding_service = EmbeddingService(
        chroma_client=chroma_client,
        s3_client=s3_client,
        text_extractor_service=text_extractor_service,
        db=None,
        model=embedding_model,
    )

    message_handler = SqsMessageHandler(embedding_service=embedding_service)
    sqs_client = SQSClient(message_handler=message_handler)
    await sqs_client.start()

    _app.state.embedding_model = embedding_model
    _app.state.chroma_client = chroma_client
    _app.state.s3_client = s3_client
    _app.state.text_extractor_service = text_extractor_service
    _app.state.embedding_service = embedding_service

    yield
    await sqs_client.stop()
    print("🔒 Application shutdown cleanup.")


def create_app() -> FastAPI:
    """Create and configure FastAPI app instance."""
    _app = FastAPI(title="Example FastAPI App", lifespan=lifespan)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Instrumentator().instrument(_app).expose(_app)

    _app.add_middleware(AuthMiddleware)

    _app.include_router(chat_router, prefix="", tags=["chat"])
    _app.include_router(ws_chat_router, tags=["websocket"])
    _app.include_router(upload_router, tags=["upload"])

    @_app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return _app


app = create_app()  # pylint redefines-outer-name
