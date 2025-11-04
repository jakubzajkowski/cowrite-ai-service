"""API endpoint for uploading files to S3 and saving metadata in the database."""

from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    File,
    Depends,
    HTTPException,
    BackgroundTasks,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.ai.chroma_client import ChromaClient
from app.services.ai.embedding_service import EmbeddingService
from app.services.files.s3_service import S3Client
from app.services.files.text_extraction_service import TextExtractionService
from app.services.files.upload_service import UploadService

router = APIRouter()


def get_text_extraction_service() -> TextExtractionService:
    """Factory for TextExtractionService."""
    return TextExtractionService()


def get_chroma_client() -> ChromaClient:
    """Factory for Chroma client."""
    return ChromaClient()


def get_s3_client() -> S3Client:
    """Factory for S3 client."""
    return S3Client()


def get_upload_service(
    s3_client: S3Client = Depends(get_s3_client),
) -> UploadService:
    """Factory for UploadService."""
    return UploadService(s3_client)


def get_embedding_service(
    s3_client: S3Client = Depends(get_s3_client),
    chroma_client: ChromaClient = Depends(get_chroma_client),
    text_extraction_service: TextExtractionService = Depends(
        get_text_extraction_service
    ),
    db: AsyncSession = Depends(get_db),
) -> EmbeddingService:
    """Factory for EmbeddingService."""
    return EmbeddingService(chroma_client, s3_client, text_extraction_service, db)


@router.post("/conversations/{conversation_id}/upload")
async def upload_file(
    request: Request,
    conversation_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    upload_service: UploadService = Depends(get_upload_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    """
    Upload a file to S3 and save metadata in the database.
    Then trigger async embedding creation in the background.
    """
    user = request.state.user if request.state.user else None

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    chat_file = await upload_service.upload_file_and_save_metadata(
        session=session, file=file, conversation_id=conversation_id, user_id=user["id"]
    )

    background_tasks.add_task(
        embedding_service.add_file_embeddings,
        file_key=chat_file.key,
        file_name=chat_file.filename,
        user_id=user["id"],
        file_id=str(chat_file.id),
    )

    return chat_file


@router.get("/conversations/upload/status/{file_id}")
async def file_status(
    file_id: str,
    session: AsyncSession = Depends(get_db),
    upload_service: UploadService = Depends(get_upload_service),
):
    """
    Get the status of a file processing.
    """
    chat_file = await upload_service.get_file_status(session=session, file_id=file_id)

    if not chat_file:
        raise HTTPException(status_code=404, detail="File not found")

    return {"file_id": chat_file.id, "status": chat_file.status}
