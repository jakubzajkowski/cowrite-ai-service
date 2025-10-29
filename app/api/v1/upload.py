"""API endpoint for uploading files to S3 and saving metadata in the database."""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.upload_service import upload_file_and_save_metadata

router = APIRouter()


@router.post("/conversations/{conversation_id}/upload")
async def upload_file(
    conversation_id: int,
    file: UploadFile = File(...),
    user_id: int = 1,
    session: AsyncSession = Depends(get_db),
):
    """
    Upload a file to S3 and save metadata in the database.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    chat_file = await upload_file_and_save_metadata(
        session=session, file=file, conversation_id=conversation_id, user_id=user_id
    )

    return {
        "id": str(chat_file.id),
        "filename": chat_file.filename,
        "file_type": chat_file.file_type,
        "size": chat_file.size,
        "storage_path": chat_file.storage_path,
    }
