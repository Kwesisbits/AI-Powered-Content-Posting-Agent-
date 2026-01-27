"""
Content generation API endpoints.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ContentGenerationRequest, ContentDraftResponse, 
    ContentDraftCreate, UserResponse
)
from app.core.agents.content_agent import ContentAgent
from app.core.workflows.approval_engine import ApprovalWorkflow
from app.core.controls.system_controls import SystemControls
from app.models import User, ContentDraft, ContentStatus
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=ContentDraftResponse)
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered content.
    
    - **platform**: Social media platform (linkedin, instagram, twitter)
    - **media_asset_ids**: Optional list of media asset IDs
    - **brand_voice_id**: Optional brand voice configuration ID
    - **context**: Optional context for generation
    - **prompt_override**: Optional custom prompt to override default
    """
    # Check system controls
    system_controls = SystemControls(db)
    await system_controls.initialize()
    
    if not system_controls.can_generate_content():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Content generation is disabled in current system mode"
        )
    
    try:
        # Initialize content agent
        content_agent = ContentAgent(db)
        
        # Generate content
        content_draft = await content_agent.generate_content(request, current_user.id)
        
        # Convert to response model
        return ContentDraftResponse.from_orm(content_draft)
        
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.get("/drafts", response_model=List[ContentDraftResponse])
async def list_content_drafts(
    status: Optional[ContentStatus] = None,
    platform: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List content drafts.
    
    - **status**: Filter by status (draft, pending_review, etc.)
    - **platform**: Filter by platform (linkedin, instagram, twitter)
    """
    query = db.query(ContentDraft)
    
    # Filter by user (clients only see their own, admins see all)
    if current_user.role == "client":
        query = query.filter(ContentDraft.created_by == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(ContentDraft.status == status)
    
    if platform:
        query = query.filter(ContentDraft.platform == platform)
    
    # Order by creation date (newest first)
    drafts = query.order_by(ContentDraft.created_at.desc()).all()
    
    return [ContentDraftResponse.from_orm(draft) for draft in drafts]


@router.get("/drafts/{draft_id}", response_model=ContentDraftResponse)
async def get_content_draft(
    draft_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific content draft by ID.
    """
    draft = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content draft #{draft_id} not found"
        )
    
    # Check permissions (clients can only view their own drafts)
    if current_user.role == "client" and draft.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this draft"
        )
    
    return ContentDraftResponse.from_orm(draft)


@router.post("/drafts/{draft_id}/regenerate", response_model=ContentDraftResponse)
async def regenerate_content_draft(
    draft_id: int,
    prompt_override: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate content for an existing draft.
    
    - **prompt_override**: Optional custom prompt for regeneration
    """
    # Check system controls
    system_controls = SystemControls(db)
    await system_controls.initialize()
    
    if not system_controls.can_generate_content():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Content generation is disabled in current system mode"
        )
    
    try:
        content_agent = ContentAgent(db)
        new_draft = await content_agent.regenerate_content(
            draft_id, 
            prompt_override
        )
        
        return ContentDraftResponse.from_orm(new_draft)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Content regeneration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content regeneration failed: {str(e)}"
        )


@router.delete("/drafts/{draft_id}")
async def delete_content_draft(
    draft_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a content draft (soft delete by archiving).
    """
    draft = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content draft #{draft_id} not found"
        )
    
    # Check permissions
    if current_user.role == "client" and draft.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this draft"
        )
    
    # Archive instead of hard delete
    draft.status = ContentStatus.ARCHIVED
    draft.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Content draft #{draft_id} archived successfully"}


@router.post("/drafts/{draft_id}/submit", response_model=ContentDraftResponse)
async def submit_for_approval(
    draft_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a content draft for approval.
    """
    try:
        approval_workflow = ApprovalWorkflow(db)
        draft, approval_request = await approval_workflow.submit_for_approval(
            draft_id, 
            current_user.id
        )
        
        return ContentDraftResponse.from_orm(draft)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to submit for approval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit for approval: {str(e)}"
        )
