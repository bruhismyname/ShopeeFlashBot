"""
Authentication endpoints for SaaS API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import logging

from ..models.user import User, UserCreate, UserLogin, UserResponse
from ..config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory storage for demo (replace with database in production)
users_db = {}
user_id_counter = 1

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    global user_id_counter
    
    # Check if user already exists
    for user in users_db.values():
        if user.email == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if user.username == user_data.username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        id=user_id_counter,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_pwd,
        subscription_tier="free"
    )
    
    users_db[user_id_counter] = new_user
    user_id_counter += 1
    
    logger.info(f"New user registered: {new_user.email}")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        subscription_tier=new_user.subscription_tier,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )

@router.post("/login")
async def login(login_data: UserLogin):
    """Login and get access token"""
    # Find user by email
    user = None
    for u in users_db.values():
        if u.email == login_data.email:
            user = u
            break
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            subscription_tier=user.subscription_tier,
            is_active=user.is_active,
            created_at=user.created_at
        )
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        subscription_tier=current_user.subscription_tier,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
