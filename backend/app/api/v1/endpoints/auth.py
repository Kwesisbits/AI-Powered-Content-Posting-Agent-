"""
Authentication API endpoints (simplified for demo).
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.database import get_db
from app.config import settings
from app.schemas import UserLogin, Token, UserResponse
from app.models import User, UserRole

router = APIRouter()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Demo users (in production, would be in database)
DEMO_USERS = {
    "admin@demo.com": {
        "id": 1,
        "email": "admin@demo.com",
        "full_name": "Admin User",
        "hashed_password": "demo123",  # In production, use bcrypt
        "role": UserRole.ADMIN,
        "is_active": True
    },
    "reviewer@demo.com": {
        "id": 2,
        "email": "reviewer@demo.com",
        "full_name": "Review
