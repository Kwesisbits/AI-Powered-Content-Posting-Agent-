"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


# =============== BASE SCHEMAS ===============
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# =============== USER SCHEMAS ===============
class UserRole(str, Enum):
    ADMIN = "admin"
    REVIEWER = "reviewer"
    CLIENT = "client"


class UserBase(BaseSchema):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.CLIENT


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseSchema):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class Token(BaseSchema):
    access_token: str
    token_type: str
    user: UserResponse


# =============== BRAND VOICE SCHEMAS ===============
class BrandVoiceConfig(BaseSchema):
    tone: str = "professional"
    target_audience: str = "general"
    key_topics: List[str] = []
    avoid_topics: List[str] = []
    hashtag_strategy: str = "3-5 relevant hashtags"
    cta_style: str = "question or value proposition"
    formality_level: int = Field(5, ge=1, le=10)
    humor_allowed: bool = False
    emoji_usage: Dict[str, str] = {  # per platform
        "linkedin": "minimal",
        "instagram": "moderate",
        "twitter": "moderate"
    }
    banned_words: List[str] = []


class BrandVoiceBase(BaseSchema):
    name: str
    description: Optional[str] = None
    config: BrandVoiceConfig


class BrandVoiceCreate(BrandVoiceBase):
    pass


class BrandVoiceResponse(BrandVoiceBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# =============== MEDIA SCHEMAS ===============
class MediaAssetBase(BaseSchema):
    filename: str
    mime_type: str
    size_bytes: int


class MediaAssetCreate(MediaAssetBase):
    pass


class MediaAssetResponse(MediaAssetBase):
    id: int
    filepath: str
    metadata: Optional[Dict[str, Any]] = None
    uploaded_by: int
    created_at: datetime


# =============== CONTENT SCHEMAS ===============
class Platform(str, Enum):
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class ContentGenerationRequest(BaseSchema):
    platform: Platform
    media_asset_ids: Optional[List[int]] = None
    brand_voice_id: Optional[int] = None
    context: Optional[str] = None
    prompt_override: Optional[str] = None


class ContentDraftBase(BaseSchema):
    platform: Platform
    content_text: str
    hashtags: Optional[List[str]] = None
    media_assets: Optional[List[int]] = None
    brand_voice_id: Optional[int] = None


class ContentDraftCreate(ContentDraftBase):
    pass


class ContentDraftResponse(ContentDraftBase):
    id: int
    status: ContentStatus
    generated_context: Optional[Dict[str, Any]] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships (optional)
    author: Optional[UserResponse] = None
    brand_voice: Optional[BrandVoiceResponse] = None


# =============== APPROVAL SCHEMAS ===============
class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class ApprovalRequestBase(BaseSchema):
    content_draft_id: int
    comments: Optional[str] = None


class ApprovalRequestCreate(ApprovalRequestBase):
    pass


class ApprovalRequestResponse(ApprovalRequestBase):
    id: int
    status: ApprovalStatus
    requested_by: int
    requested_at: datetime
    reviewer_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    
    # Relationships
    content_draft: Optional[ContentDraftResponse] = None


class ApprovalAction(BaseSchema):
    action: ApprovalStatus
    comments: Optional[str] = None


# =============== CONTROL SCHEMAS ===============
class SystemMode(str, Enum):
    NORMAL = "normal"
    MANUAL = "manual"
    CRISIS = "crisis"


class SystemStatusBase(BaseSchema):
    mode: SystemMode
    is_paused: bool
    notes: Optional[str] = None


class SystemStatusResponse(SystemStatusBase):
    last_updated_by: Optional[int] = None
    last_updated_at: datetime


class ControlAction(BaseSchema):
    action: str  # pause, resume, set_manual, set_crisis, set_normal
    notes: Optional[str] = None


# =============== SCHEDULING SCHEMAS ===============
class SchedulePostRequest(BaseSchema):
    content_draft_id: int
    platform: Platform
    scheduled_for: datetime


class ScheduledPostResponse(BaseSchema):
    id: int
    content_draft_id: int
    platform: Platform
    scheduled_for: datetime
    posted_at: Optional[datetime] = None
    status: str
    post_id: Optional[str] = None
    created_at: datetime


# =============== AUDIT LOG SCHEMAS ===============
class AuditLogResponse(BaseSchema):
    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


# =============== HEALTH CHECK ===============
class HealthCheck(BaseSchema):
    status: str
    timestamp: datetime
    version: str
    database: bool
    ollama: Optional[bool] = None
    system_mode: SystemMode
