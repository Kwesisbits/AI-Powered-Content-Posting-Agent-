"""
Approval workflow API endpoints.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ApprovalRequestResponse, ApprovalRequestCreate, 
    ApprovalAction, ContentDraftResponse, UserResponse
)
from app.models import ApprovalRequest, ApprovalStatus, UserRole
from app.api.v1.endpoints.auth import get_current_user
from app.core.workflows.approval_engine import ApprovalWorkflow

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/request", response_model=ApprovalRequestResponse)
async def create_approval_request(
    request: ApprovalRequestCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create an approval request for a content draft.
    
    - **content_draft_id**: ID of draft to submit for approval
    - **comments**: Optional comments for the reviewer
    """
    try:
        approval_workflow = ApprovalWorkflow(db)
        draft, approval_request = await approval_workflow.submit_for_approval(
            request.content_draft_id,
            current_user.id
        )
        
        return ApprovalRequestResponse.from_orm(approval_request)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create approval request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create approval request: {str(e)}"
        )


@router.get("/pending", response_model=List[ApprovalRequestResponse])
async def get_pending_approvals(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pending approval requests.
    
    - Reviewers see all pending requests
    - Clients see only their own pending requests
    """
    approval_workflow = ApprovalWorkflow(db)
    
    if current_user.role in [UserRole.ADMIN, UserRole.REVIEWER]:
        # Admins and reviewers see all pending
        approvals = await approval_workflow.get_pending_approvals()
    else:
        # Clients see only their own
        approvals = await approval_workflow.get_pending_approvals(current_user.id)
    
    return [ApprovalRequestResponse.from_orm(approval) for approval in approvals]


@router.post("/{approval_id}/action", response_model=ContentDraftResponse)
async def process_approval(
    approval_id: int,
    action: ApprovalAction,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process an approval request (approve, reject, request changes).
    
    - **approval_id**: ID of approval request
    - **action**: Action to take (approve, reject, changes_requested)
    - **comments**: Optional comments for the decision
    """
    # Only reviewers and admins can process approvals
    if current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only reviewers and admins can process approvals"
        )
    
    try:
        approval_workflow = ApprovalWorkflow(db)
        draft, approval_request = await approval_workflow.process_approval(
            approval_id,
            action,
            current_user.id
        )
        
        return ContentDraftResponse.from_orm(draft)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to process approval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process approval: {str(e)}"
        )


@router.get("/draft/{draft_id}", response_model=List[ApprovalRequestResponse])
async def get_draft_approval_history(
    draft_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get approval history for a specific draft.
    
    - **draft_id**: ID of content draft
    """
    # Check permissions
    draft = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft #{draft_id} not found"
        )
    
    if current_user.role == "client" and draft.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this draft's approval history"
        )
    
    approval_workflow = ApprovalWorkflow(db)
    history = approval_workflow.get_approval_history(draft_id)
    
    return [ApprovalRequestResponse.from_orm(approval) for approval in history]


@router.post("/draft/{draft_id}/request-changes", response_model=ContentDraftResponse)
async def request_changes_on_draft(
    draft_id: int,
    comments: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request changes on a draft.
    
    - **draft_id**: ID of content draft
    - **comments**: Change requests
    """
    # Only reviewers and admins can request changes
    if current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only reviewers and admins can request changes"
        )
    
    try:
        approval_workflow = ApprovalWorkflow(db)
        draft = await approval_workflow.request_changes(
            draft_id,
            current_user.id,
            comments
        )
        
        return ContentDraftResponse.from_orm(draft)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to request changes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request changes: {str(e)}"
        )
