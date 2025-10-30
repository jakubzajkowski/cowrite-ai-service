"""API endpoint for uploading files to S3 and saving metadata in the database."""

from fastapi import APIRouter, Request, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.files.s3_service import S3Client
from app.services.files.upload_service import UploadService

router = APIRouter()


def get_s3_client() -> S3Client:
    """Factory for S3 client."""
    return S3Client()


def get_upload_service(
    s3_client: S3Client = Depends(get_s3_client),
) -> UploadService:
    """Factory for UploadService."""
    return UploadService(s3_client)


@router.post("/conversations/{conversation_id}/upload")
async def upload_file(
    request: Request,
    conversation_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    upload_service: UploadService = Depends(get_upload_service),
):
    """
    Upload a file to S3 and save metadata in the database.
    """
    user = request.state.user if request.state.user else None

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    chat_file = await upload_service.upload_file_and_save_metadata(
        session=session, file=file, conversation_id=conversation_id, user_id=user["id"]
    )

    return {
        "id": str(chat_file.id),
        "filename": chat_file.filename,
        "file_type": chat_file.file_type,
        "size": chat_file.size,
        "storage_path": chat_file.storage_path,
    }
