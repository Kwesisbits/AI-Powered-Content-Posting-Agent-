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
        "full_name": "Reviewer User",
        "hashed_password": "demo123",
        "role": UserRole.REVIEWER,
        "is_active": True
    },
    "client@demo.com": {
        "id": 3,
        "email": "client@demo.com",
        "full_name": "Client User",
        "hashed_password": "demo123",
        "role": UserRole.CLIENT,
        "is_active": True
    }
}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserResponse:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from demo data
    user_data = DEMO_USERS.get(email)
    if user_data is None:
        raise credentials_exception
    
    return UserResponse(**user_data)


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint (simplified for demo)."""
    # Check if user exists in demo data
    user_data = DEMO_USERS.get(form_data.username)
    
    if not user_data or user_data["hashed_password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["email"]}, 
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user_data)
    )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user
