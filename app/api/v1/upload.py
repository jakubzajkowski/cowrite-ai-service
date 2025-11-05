"""
API endpoint for uploading files to S3 and saving metadata in the database.
"""

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
from app.services.ai.embedding_service import EmbeddingService
from app.services.files.s3_service import S3Client
from app.services.files.text_extraction_service import TextExtractionService
from app.services.files.upload_service import UploadService

router = APIRouter()


def get_s3_client(request: Request) -> S3Client:
    """Return preloaded S3Client from app.state."""
    return request.app.state.s3_client


def get_text_extraction_service(request: Request) -> TextExtractionService:
    """Return preloaded TextExtractionService from app.state."""
    return request.app.state.text_extractor_service


def get_embedding_service(
    request: Request, db: AsyncSession = Depends(get_db)
) -> EmbeddingService:
    """Return EmbeddingService using preloaded objects from app.state."""
    return EmbeddingService(
        chroma_client=request.app.state.chroma_client,
        s3_client=request.app.state.s3_client,
        text_extractor_service=request.app.state.text_extractor_service,
        db=db,
        model=request.app.state.embedding_model,
    )


def get_upload_service(request: Request) -> UploadService:
    """Return UploadService using preloaded S3 client from app.state."""
    return UploadService(request.app.state.s3_client)


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
    user = getattr(request.state, "user", None)

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

    return {"fileId": chat_file.id, "status": chat_file.status}
