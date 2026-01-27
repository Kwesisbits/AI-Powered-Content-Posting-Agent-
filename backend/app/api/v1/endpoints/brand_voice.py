"""
Brand voice management API endpoints.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import BrandVoiceCreate, BrandVoiceResponse, UserResponse
from app.models import BrandVoice, UserRole
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=BrandVoiceResponse)
async def create_brand_voice(
    brand_voice: BrandVoiceCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new brand voice configuration.
    
    - **name**: Name of the brand voice
    - **description**: Optional description
    - **config**: Brand voice configuration
    """
    # Only admins can create brand voices
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create brand voices"
        )
    
    # Check if brand voice with same name exists
    existing = db.query(BrandVoice).filter(
        BrandVoice.name == brand_voice.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Brand voice '{brand_voice.name}' already exists"
        )
    
    try:
        # Create brand voice
        new_brand_voice = BrandVoice(
            name=brand_voice.name,
            description=brand_voice.description,
            config=brand_voice.config.dict(),
            created_by=current_user.id,
            is_active=True
        )
        
        db.add(new_brand_voice)
        db.commit()
        db.refresh(new_brand_voice)
        
        logger.info(f"Created brand voice '{brand_voice.name}' by user #{current_user.id}")
        
        return BrandVoiceResponse.from_orm(new_brand_voice)
        
    except Exception as e:
        logger.error(f"Failed to create brand voice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create brand voice: {str(e)}"
        )


@router.get("/", response_model=List[BrandVoiceResponse])
async def list_brand_voices(
    active_only: bool = True,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List brand voice configurations.
    
    - **active_only**: Only return active brand voices
    """
    query = db.query(BrandVoice)
    
    if active_only:
        query = query.filter(BrandVoice.is_active == True)
    
    brand_voices = query.order_by(BrandVoice.name.asc()).all()
    
    return [BrandVoiceResponse.from_orm(bv) for bv in brand_voices]


@router.get("/{brand_voice_id}", response_model=BrandVoiceResponse)
async def get_brand_voice(
    brand_voice_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific brand voice configuration."""
    brand_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
    
    if not brand_voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand voice #{brand_voice_id} not found"
        )
    
    # Check if active
    if not brand_voice.is_active:
        # Only admins can view inactive brand voices
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view inactive brand voices"
            )
    
    return BrandVoiceResponse.from_orm(brand_voice)


@router.put("/{brand_voice_id}", response_model=BrandVoiceResponse)
async def update_brand_voice(
    brand_voice_id: int,
    brand_voice_update: BrandVoiceCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update brand voice configuration."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update brand voices"
        )
    
    brand_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
    
    if not brand_voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand voice #{brand_voice_id} not found"
        )
    
    # Check name uniqueness
    if brand_voice_update.name != brand_voice.name:
        existing = db.query(BrandVoice).filter(
            BrandVoice.name == brand_voice_update.name,
            BrandVoice.id != brand_voice_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Brand voice '{brand_voice_update.name}' already exists"
            )
    
    try:
        # Update brand voice
        brand_voice.name = brand_voice_update.name
        brand_voice.description = brand_voice_update.description
        brand_voice.config = brand_voice_update.config.dict()
        
        db.commit()
        db.refresh(brand_voice)
        
        logger.info(f"Updated brand voice #{brand_voice_id} by user #{current_user.id}")
        
        return BrandVoiceResponse.from_orm(brand_voice)
        
    except Exception as e:
        logger.error(f"Failed to update brand voice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update brand voice: {str(e)}"
        )


@router.delete("/{brand_voice_id}")
async def delete_brand_voice(
    brand_voice_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete (deactivate) brand voice configuration."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete brand voices"
        )
    
    brand_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
    
    if not brand_voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand voice #{brand_voice_id} not found"
        )
    
    # Soft delete by deactivating
    brand_voice.is_active = False
    
    db.commit()
    
    logger.info(f"Deleted (deactivated) brand voice #{brand_voice_id} by user #{current_user.id}")
    
    return {"message": f"Brand voice #{brand_voice_id} deleted successfully"}
