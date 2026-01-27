"""
Approval workflow engine with state machine.
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session

from app.models import (
    ContentDraft, ApprovalRequest, User, 
    ContentStatus, ApprovalStatus, UserRole
)
from app.schemas import ApprovalAction

logger = logging.getLogger(__name__)


class ApprovalWorkflow:
    """Approval workflow state machine."""
    
    # State transitions
    TRANSITIONS: Dict[ContentStatus, List[ContentStatus]] = {
        ContentStatus.DRAFT: [ContentStatus.PENDING_REVIEW, ContentStatus.ARCHIVED],
        ContentStatus.PENDING_REVIEW: [
            ContentStatus.APPROVED, 
            ContentStatus.REJECTED, 
            ContentStatus.CHANGES_REQUESTED,
            ContentStatus.ARCHIVED
        ],
        ContentStatus.CHANGES_REQUESTED: [
            ContentStatus.DRAFT, 
            ContentStatus.PENDING_REVIEW,
            ContentStatus.ARCHIVED
        ],
        ContentStatus.APPROVED: [
            ContentStatus.SCHEDULED, 
            ContentStatus.ARCHIVED,
            ContentStatus.CANCELLED
        ],
        ContentStatus.REJECTED: [ContentStatus.ARCHIVED],
        ContentStatus.SCHEDULED: [
            ContentStatus.PUBLISHED, 
            ContentStatus.CANCELLED,
            ContentStatus.ARCHIVED
        ],
        ContentStatus.PUBLISHED: [ContentStatus.ARCHIVED],
        ContentStatus.CANCELLED: [ContentStatus.ARCHIVED],
        ContentStatus.ARCHIVED: []
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def can_transition(
        self, 
        current_status: ContentStatus, 
        target_status: ContentStatus
    ) -> bool:
        """Check if transition is allowed."""
        allowed = self.TRANSITIONS.get(current_status, [])
        return target_status in allowed
    
    async def submit_for_approval(
        self, 
        draft_id: int, 
        user_id: int
    ) -> Tuple[ContentDraft, ApprovalRequest]:
        """
        Submit content draft for approval.
        
        Args:
            draft_id: Content draft ID
            user_id: User ID submitting for approval
            
        Returns:
            Tuple of (updated draft, approval request)
        """
        draft = self.db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
        if not draft:
            raise ValueError(f"Draft #{draft_id} not found")
        
        # Check current status
        if draft.status != ContentStatus.DRAFT:
            raise ValueError(f"Draft #{draft_id} is not in DRAFT status")
        
        # Check if user is author
        if draft.created_by != user_id:
            # Log but allow (in real system would check permissions)
            logger.warning(f"User #{user_id} submitting draft #{draft_id} not created by them")
        
        # Update draft status
        draft.status = ContentStatus.PENDING_REVIEW
        draft.updated_at = datetime.utcnow()
        
        # Create approval request
        approval_request = ApprovalRequest(
            content_draft_id=draft_id,
            requested_by=user_id,
            requested_at=datetime.utcnow(),
            status=ApprovalStatus.PENDING
        )
        
        self.db.add(approval_request)
        self.db.commit()
        self.db.refresh(draft)
        self.db.refresh(approval_request)
        
        logger.info(f"Draft #{draft_id} submitted for approval by user #{user_id}")
        
        return draft, approval_request
    
    async def process_approval(
        self, 
        approval_request_id: int, 
        action: ApprovalAction,
        reviewer_id: int
    ) -> Tuple[ContentDraft, ApprovalRequest]:
        """
        Process approval decision.
        
        Args:
            approval_request_id: Approval request ID
            action: Approval action (approve/reject/request changes)
            reviewer_id: User ID of reviewer
            
        Returns:
            Tuple of (updated draft, updated approval request)
        """
        # Get approval request
        approval_request = self.db.query(ApprovalRequest).filter(
            ApprovalRequest.id == approval_request_id
        ).first()
        
        if not approval_request:
            raise ValueError(f"Approval request #{approval_request_id} not found")
        
        # Check if already processed
        if approval_request.status != ApprovalStatus.PENDING:
            raise ValueError(f"Approval request #{approval_request_id} already processed")
        
        # Get associated draft
        draft = approval_request.content_draft
        
        # Update approval request
        approval_request.reviewer_id = reviewer_id
        approval_request.status = action.action
        approval_request.comments = action.comments
        approval_request.reviewed_at = datetime.utcnow()
        
        # Update draft status based on action
        if action.action == ApprovalStatus.APPROVED:
            new_status = ContentStatus.APPROVED
        elif action.action == ApprovalStatus.REJECTED:
            new_status = ContentStatus.REJECTED
        elif action.action == ApprovalStatus.CHANGES_REQUESTED:
            new_status = ContentStatus.CHANGES_REQUESTED
        else:
            raise ValueError(f"Invalid action: {action.action}")
        
        # Validate transition
        if not self.can_transition(draft.status, new_status):
            raise ValueError(
                f"Cannot transition draft #{draft.id} from {draft.status} to {new_status}"
            )
        
        # Update draft
        draft.status = new_status
        draft.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(draft)
        self.db.refresh(approval_request)
        
        # Log action
        action_map = {
            ApprovalStatus.APPROVED: "approved",
            ApprovalStatus.REJECTED: "rejected",
            ApprovalStatus.CHANGES_REQUESTED: "requested changes on"
        }
        
        logger.info(
            f"Reviewer #{reviewer_id} {action_map[action.action]} "
            f"draft #{draft.id} (approval request #{approval_request_id})"
        )
        
        return draft, approval_request
    
    async def request_changes(
        self, 
        draft_id: int, 
        reviewer_id: int,
        comments: str
    ) -> ContentDraft:
        """
        Request changes on a draft (alternative to approval request).
        
        Args:
            draft_id: Content draft ID
            reviewer_id: User ID requesting changes
            comments: Change requests
            
        Returns:
            Updated draft
        """
        draft = self.db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
        if not draft:
            raise ValueError(f"Draft #{draft_id} not found")
        
        # Check if draft is in reviewable state
        if draft.status not in [ContentStatus.PENDING_REVIEW, ContentStatus.CHANGES_REQUESTED]:
            raise ValueError(f"Draft #{draft_id} not in reviewable state")
        
        # Update draft
        draft.status = ContentStatus.CHANGES_REQUESTED
        draft.updated_at = datetime.utcnow()
        
        # Create or update approval request
        approval_request = self.db.query(ApprovalRequest).filter(
            ApprovalRequest.content_draft_id == draft_id,
            ApprovalRequest.status == ApprovalStatus.PENDING
        ).first()
        
        if approval_request:
            approval_request.status = ApprovalStatus.CHANGES_REQUESTED
            approval_request.reviewer_id = reviewer_id
            approval_request.comments = comments
            approval_request.reviewed_at = datetime.utcnow()
        else:
            approval_request = ApprovalRequest(
                content_draft_id=draft_id,
                requested_by=reviewer_id,
                reviewer_id=reviewer_id,
                status=ApprovalStatus.CHANGES_REQUESTED,
                comments=comments,
                reviewed_at=datetime.utcnow()
            )
            self.db.add(approval_request)
        
        self.db.commit()
        self.db.refresh(draft)
        
        logger.info(f"Changes requested on draft #{draft_id} by reviewer #{reviewer_id}")
        
        return draft
    
    def get_approval_history(self, draft_id: int) -> List[ApprovalRequest]:
        """Get approval history for a draft."""
        return self.db.query(ApprovalRequest).filter(
            ApprovalRequest.content_draft_id == draft_id
        ).order_by(ApprovalRequest.requested_at.desc()).all()
    
    async def get_pending_approvals(
        self, 
        reviewer_id: Optional[int] = None
    ) -> List[ApprovalRequest]:
        """Get pending approval requests."""
        query = self.db.query(ApprovalRequest).filter(
            ApprovalRequest.status == ApprovalStatus.PENDING
        )
        
        if reviewer_id:
            query = query.filter(ApprovalRequest.reviewer_id == reviewer_id)
        
        return query.order_by(ApprovalRequest.requested_at.asc()).all()
