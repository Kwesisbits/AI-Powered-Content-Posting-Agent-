"""
Media upload and management API endpoints.
"""
import logging
import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.schemas import MediaAssetResponse
from app.models import MediaAsset
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=MediaAssetResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload media file (image/video).
    
    - **file**: Media file to upload
    """
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    try:
        # Save file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Create media asset record
        media_asset = MediaAsset(
            filename=file.filename,
            filepath=filepath,
            mime_type=file.content_type,
            size_bytes=file_size,
            uploaded_by=current_user.id
        )
        
        db.add(media_asset)
        db.commit()
        db.refresh(media_asset)
        
        logger.info(f"Media uploaded: {file.filename} ({file_size} bytes) by user #{current_user.id}")
        
        return MediaAssetResponse.from_orm(media_asset)
        
    except Exception as e:
        # Clean up file if upload failed
        if os.path.exists(filepath):
            os.remove(filepath)
        
        logger.error(f"Media upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Media upload failed: {str(e)}"
        )


@router.get("/", response_model=List[MediaAssetResponse])
async def list_media_assets(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List uploaded media assets."""
    # Clients only see their own uploads
    if current_user.role == "client":
        media_assets = db.query(MediaAsset).filter(
            MediaAsset.uploaded_by == current_user.id
        ).all()
    else:
        # Admins and reviewers see all
        media_assets = db.query(MediaAsset).all()
    
    return [MediaAssetResponse.from_orm(asset) for asset in media_assets]


@router.get("/{asset_id}", response_model=MediaAssetResponse)
async def get_media_asset(
    asset_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific media asset."""
    media_asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    
    if not media_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media asset #{asset_id} not found"
        )
    
    # Check permissions
    if current_user.role == "client" and media_asset.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this media asset"
        )
    
    return MediaAssetResponse.from_orm(media_asset)
