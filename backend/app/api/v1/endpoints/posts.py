"""
Post scheduling and management API endpoints.
"""
import logging
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SchedulePostRequest, ScheduledPostResponse, UserResponse
from app.models import (
    ScheduledPost, ContentDraft, ContentStatus, 
    Platform, UserRole, SystemMode
)
from app.api.v1.endpoints.auth import get_current_user
from app.core.controls.system_controls import SystemControls
from app.core.workflows.approval_engine import ApprovalWorkflow

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/schedule", response_model=ScheduledPostResponse)
async def schedule_post(
    request: SchedulePostRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Schedule a post for publishing.
    
    - **content_draft_id**: ID of approved content draft
    - **platform**: Platform to post to
    - **scheduled_for**: When to schedule the post
    """
    # Check system controls
    system_controls = SystemControls(db)
    await system_controls.initialize()
    
    if not system_controls.can_auto_post():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Auto-posting is disabled in current system mode"
        )
    
    # Get the content draft
    draft = db.query(ContentDraft).filter(ContentDraft.id == request.content_draft_id).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content draft #{request.content_draft_id} not found"
        )
    
    # Check if draft is approved
    if draft.status != ContentStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Draft must be approved. Current status: {draft.status}"
        )
    
    # Check permissions
    if current_user.role == "client" and draft.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to schedule this draft"
        )
    
    # Check scheduling time (must be in future)
    if request.scheduled_for < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduled time must be in the future"
        )
    
    try:
        # Create scheduled post
        scheduled_post = ScheduledPost(
            content_draft_id=request.content_draft_id,
            platform=request.platform,
            scheduled_for=request.scheduled_for,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        db.add(scheduled_post)
        
        # Update draft status
        draft.status = ContentStatus.SCHEDULED
        draft.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(scheduled_post)
        
        # Schedule background task for posting
        background_tasks.add_task(
            _process_scheduled_post,
            scheduled_post.id,
            db
        )
        
        logger.info(
            f"Scheduled post #{scheduled_post.id} for "
            f"{request.platform} at {request.scheduled_for}"
        )
        
        return ScheduledPostResponse.from_orm(scheduled_post)
        
    except Exception as e:
        logger.error(f"Failed to schedule post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule post: {str(e)}"
        )


@router.get("/scheduled", response_model=List[ScheduledPostResponse])
async def get_scheduled_posts(
    status: str = "pending",
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get scheduled posts.
    
    - **status**: Filter by status (pending, posted, failed, cancelled)
    """
    query = db.query(ScheduledPost)
    
    # Apply status filter
    if status:
        query = query.filter(ScheduledPost.status == status)
    
    # Apply permissions filter
    if current_user.role == "client":
        # Clients only see posts from their drafts
        query = query.join(ContentDraft).filter(
            ContentDraft.created_by == current_user.id
        )
    
    # Order by scheduled time
    scheduled_posts = query.order_by(ScheduledPost.scheduled_for.asc()).all()
    
    return [ScheduledPostResponse.from_orm(post) for post in scheduled_posts]


@router.post("/{post_id}/cancel")
async def cancel_scheduled_post(
    post_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a scheduled post."""
    scheduled_post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    
    if not scheduled_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled post #{post_id} not found"
        )
    
    # Check permissions
    if current_user.role == "client":
        draft = scheduled_post.content_draft
        if draft.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this post"
            )
    
    # Update status
    scheduled_post.status = "cancelled"
    
    # Update draft status back to approved
    draft = scheduled_post.content_draft
    draft.status = ContentStatus.APPROVED
    draft.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Cancelled scheduled post #{post_id}")
    
    return {"message": f"Scheduled post #{post_id} cancelled successfully"}


@router.post("/publish-now/{draft_id}", response_model=ScheduledPostResponse)
async def publish_now(
    draft_id: int,
    platform: Platform,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a draft immediately."""
    # Check system controls
    system_controls = SystemControls(db)
    await system_controls.initialize()
    
    if system_controls.is_paused or system_controls.is_crisis_mode():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Cannot publish while system is paused or in crisis mode"
        )
    
    # Get the draft
    draft = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content draft #{draft_id} not found"
        )
    
    # Check if draft is approved
    if draft.status != ContentStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Draft must be approved. Current status: {draft.status}"
        )
    
    # Check permissions
    if current_user.role == "client" and draft.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this draft"
        )
    
    try:
        # Create scheduled post for immediate publishing
        scheduled_post = ScheduledPost(
            content_draft_id=draft_id,
            platform=platform,
            scheduled_for=datetime.utcnow(),
            status="pending",
            created_at=datetime.utcnow()
        )
        
        db.add(scheduled_post)
        
        # Update draft status
        draft.status = ContentStatus.SCHEDULED
        draft.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(scheduled_post)
        
        # Process immediately
        await _process_scheduled_post(scheduled_post.id, db)
        
        return ScheduledPostResponse.from_orm(scheduled_post)
        
    except Exception as e:
        logger.error(f"Failed to publish immediately: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish immediately: {str(e)}"
        )


async def _process_scheduled_post(post_id: int, db: Session):
    """Background task to process scheduled posts."""
    from app.core.controls.system_controls import SystemControls
    
    logger.info(f"Processing scheduled post #{post_id}")
    
    try:
        # Get fresh database session
        from app.database import SessionLocal
        db = SessionLocal()
        
        scheduled_post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
        
        if not scheduled_post or scheduled_post.status != "pending":
            return
        
        # Check system controls
        system_controls = SystemControls(db)
        await system_controls.initialize()
        
        if system_controls.is_paused or system_controls.is_crisis_mode():
            logger.info(f"Post #{post_id} processing delayed due to system controls")
            # Reschedule for later
            scheduled_post.scheduled_for = datetime.utcnow() + timedelta(minutes=5)
            db.commit()
            return
        
        # Wait until scheduled time
        now = datetime.utcnow()
        if scheduled_post.scheduled_for > now:
            wait_seconds = (scheduled_post.scheduled_for - now).total_seconds()
            if wait_seconds > 0:
                import asyncio
                await asyncio.sleep(wait_seconds)
        
        # Mock post to platform
        success = await _mock_post_to_platform(
            scheduled_post.content_draft,
            scheduled_post.platform
        )
        
        if success:
            scheduled_post.status = "posted"
            scheduled_post.posted_at = datetime.utcnow()
            scheduled_post.post_id = f"mock_post_{post_id}"
            scheduled_post.metrics = {
                "impressions": 1000,
                "engagement": 50,
                "likes": 42,
                "shares": 8,
                "comments": 3
            }
            
            # Update draft status
            draft = scheduled_post.content_draft
            draft.status = ContentStatus.PUBLISHED
            draft.updated_at = datetime.utcnow()
            
            logger.info(f"Successfully posted #{post_id} to {scheduled_post.platform}")
        else:
            scheduled_post.status = "failed"
            scheduled_post.error_message = "Mock posting failed"
            
            logger.error(f"Failed to post #{post_id} to {scheduled_post.platform}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error processing scheduled post #{post_id}: {str(e)}")
        
        try:
            scheduled_post.status = "failed"
            scheduled_post.error_message = str(e)
            db.commit()
        except:
            pass
    
    finally:
        db.close()


async def _mock_post_to_platform(draft, platform: Platform) -> bool:
    """Mock posting to social platform."""
    import random
    import asyncio
    
    # Simulate API call delay
    await asyncio.sleep(random.uniform(0.5, 2.0))
    
    # Simulate 90% success rate
    return random.random() > 0.1
