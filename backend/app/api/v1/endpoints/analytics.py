"""
Analytics API endpoints (mock for demo).
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.schemas import UserResponse
from app.models import (
    ScheduledPost, ContentDraft, ContentStatus, 
    Platform, UserRole, AuditLog
)
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/posts")
async def get_post_analytics(
    days: int = 30,
    platform: Platform = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get posting analytics.
    
    - **days**: Number of days to look back (default: 30)
    - **platform**: Filter by platform
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Base query
    query = db.query(ScheduledPost).filter(
        ScheduledPost.posted_at >= start_date,
        ScheduledPost.posted_at <= end_date,
        ScheduledPost.status == "posted"
    )
    
    # Apply platform filter
    if platform:
        query = query.filter(ScheduledPost.platform == platform)
    
    # Apply permissions filter
    if current_user.role == "client":
        query = query.join(ContentDraft).filter(
            ContentDraft.created_by == current_user.id
        )
    
    posts = query.all()
    
    # Calculate analytics
    total_posts = len(posts)
    
    if total_posts == 0:
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "total_posts": 0,
            "message": "No posts found in the specified period"
        }
    
    # Platform distribution
    platform_distribution = {}
    for post in posts:
        platform_name = post.platform.value
        platform_distribution[platform_name] = platform_distribution.get(platform_name, 0) + 1
    
    # Calculate average metrics
    total_impressions = 0
    total_engagement = 0
    total_likes = 0
    total_shares = 0
    total_comments = 0
    
    for post in posts:
        if post.metrics:
            metrics = post.metrics
            total_impressions += metrics.get("impressions", 0)
            total_engagement += metrics.get("engagement", 0)
            total_likes += metrics.get("likes", 0)
            total_shares += metrics.get("shares", 0)
            total_comments += metrics.get("comments", 0)
    
    # Mock growth data (would come from real analytics in production)
    growth_data = []
    for i in range(days, 0, -1):
        date = end_date - timedelta(days=i)
        growth_data.append({
            "date": date.isoformat(),
            "posts": len([p for p in posts if p.posted_at.date() == date.date()]),
            "impressions": 500 + (i * 50) + (hash(str(date.date())) % 200),
            "engagement": 25 + (i * 3) + (hash(str(date.date())) % 50)
        })
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": days
        },
        "total_posts": total_posts,
        "platform_distribution": platform_distribution,
        "average_metrics": {
            "impressions": total_impressions // total_posts,
            "engagement": total_engagement // total_posts,
            "likes": total_likes // total_posts,
            "shares": total_shares // total_posts,
            "comments": total_comments // total_posts
        },
        "top_performing_posts": [
            {
                "id": post.id,
                "platform": post.platform.value,
                "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                "metrics": post.metrics or {},
                "content_preview": post.content_draft.content_text[:100] + "..." if post.content_draft else ""
            }
            for post in sorted(posts, key=lambda p: p.metrics.get("engagement", 0) if p.metrics else 0, reverse=True)[:5]
        ],
        "growth_data": growth_data,
        "success_rate": len([p for p in posts if p.status == "posted"]) / max(len(posts), 1) * 100
    }


@router.get("/workflow")
async def get_workflow_analytics(
    days: int = 30,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get workflow analytics.
    
    - **days**: Number of days to look back
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and reviewers can view workflow analytics"
        )
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get content drafts in period
    drafts = db.query(ContentDraft).filter(
        ContentDraft.created_at >= start_date,
        ContentDraft.created_at <= end_date
    ).all()
    
    # Calculate status distribution
    status_counts = {}
    for draft in drafts:
        status = draft.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Calculate approval metrics
    from app.models import ApprovalRequest, ApprovalStatus
    approval_requests = db.query(ApprovalRequest).filter(
        ApprovalRequest.requested_at >= start_date,
        ApprovalRequest.requested_at <= end_date
    ).all()
    
    approval_stats = {
        "total_requests": len(approval_requests),
        "approved": len([r for r in approval_requests if r.status == ApprovalStatus.APPROVED]),
        "rejected": len([r for r in approval_requests if r.status == ApprovalStatus.REJECTED]),
        "changes_requested": len([r for r in approval_requests if r.status == ApprovalStatus.CHANGES_REQUESTED]),
        "pending": len([r for r in approval_requests if r.status == ApprovalStatus.PENDING])
    }
    
    # Calculate average time metrics (mock for demo)
    avg_generation_time = 45  # seconds
    avg_approval_time = 3600  # 1 hour in seconds
    avg_publish_time = 7200   # 2 hours in seconds
    
    # User activity
    user_activity = []
    for draft in drafts:
        user_activity.append({
            "user_id": draft.created_by,
            "drafts_created": len([d for d in drafts if d.created_by == draft.created_by]),
            "last_activity": draft.created_at.isoformat()
        })
    
    # Remove duplicates
    user_activity = list({item["user_id"]: item for item in user_activity}.values())
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": days
        },
        "content_metrics": {
            "total_drafts": len(drafts),
            "status_distribution": status_counts,
            "platform_distribution": {
                "linkedin": len([d for d in drafts if d.platform == Platform.LINKEDIN]),
                "instagram": len([d for d in drafts if d.platform == Platform.INSTAGRAM]),
                "twitter": len([d for d in drafts if d.platform == Platform.TWITTER])
            }
        },
        "approval_metrics": approval_stats,
        "performance_metrics": {
            "avg_generation_time_seconds": avg_generation_time,
            "avg_approval_time_seconds": avg_approval_time,
            "avg_publish_time_seconds": avg_publish_time,
            "automation_rate": 85.5,  # percentage
            "error_rate": 2.3  # percentage
        },
        "user_activity": user_activity[:10],  # Top 10 users
        "efficiency_gain": "3.2x"  # Mock efficiency gain
    }


@router.get("/system")
async def get_system_analytics(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system analytics (admin only).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view system analytics"
        )
    
    # Get audit logs for recent activity
    recent_logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).limit(100).all()
    
    # Calculate system metrics
    total_drafts = db.query(ContentDraft).count()
    total_posts = db.query(ScheduledPost).filter(
        ScheduledPost.status == "posted"
    ).count()
    
    # Mock AI usage metrics
    ai_usage = {
        "total_requests": total_drafts * 1.5,  # Estimated
        "success_rate": 95.7,
        "avg_response_time_ms": 2450,
        "cost_saved_vs_api": 125.50,  # USD
        "models_used": ["gemma:7b", "mock"],
        "tokens_processed": total_drafts * 500  # Estimated
    }
    
    # System health
    from app.core.llm import llm_provider_factory
    from app.core.controls.system_controls import SystemControls
    
    system_controls = SystemControls(db)
    await system_controls.initialize()
    
    llm_provider = llm_provider_factory.create_provider()
    llm_available = await llm_provider.is_available()
    
    return {
        "system_health": {
            "database": True,
            "llm_service": llm_available,
            "file_storage": True,
            "system_mode": system_controls.get_mode().value,
            "uptime": "99.8%",  # Mock
            "last_incident": None
        },
        "usage_statistics": {
            "total_drafts": total_drafts,
            "total_posts": total_posts,
            "total_users": 3,  # Demo users
            "active_users_last_7_days": 3,
            "storage_used_mb": 42.5  # Mock
        },
        "ai_metrics": ai_usage,
        "recent_activity": [
            {
                "timestamp": log.timestamp.isoformat(),
                "action": log.action,
                "user_id": log.user_id,
                "details": log.details
            }
            for log in recent_logs[:20]
        ],
        "control_metrics": {
            "total_pause_events": len([l for l in recent_logs if "pause" in l.action]),
            "total_crisis_events": len([l for l in recent_logs if "crisis" in l.action]),
            "current_mode": system_controls.get_mode().value,
            "is_paused": system_controls.is_paused
        }
    }
