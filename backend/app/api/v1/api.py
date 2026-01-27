"""
API router configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, content, media, approval, control, posts, analytics
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(approval.router, prefix="/approval", tags=["approval"])
api_router.include_router(control.router, prefix="/control", tags=["control"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
