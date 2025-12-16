"""
User model for SaaS platform
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    """User model"""
    id: Optional[int] = None
    email: EmailStr
    username: str
    hashed_password: str
    subscription_tier: str = "free"
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response schema (without password)"""
    id: int
    email: str
    username: str
    subscription_tier: str
    is_active: bool
    created_at: datetime
