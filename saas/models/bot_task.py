"""
Bot task model for SaaS platform
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BotTask(BaseModel):
    """Bot task model"""
    id: Optional[int] = None
    user_id: int
    name: str
    url: str
    target_time: str
    config: Dict[str, Any] = {}
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class BotTaskCreate(BaseModel):
    """Bot task creation schema"""
    name: str
    url: str
    target_time: str
    config: Dict[str, Any] = {}

class BotTaskResponse(BaseModel):
    """Bot task response schema"""
    id: int
    user_id: int
    name: str
    url: str
    target_time: str
    status: str
    created_at: datetime
    updated_at: datetime
