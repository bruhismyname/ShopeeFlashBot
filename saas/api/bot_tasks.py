"""
Bot tasks endpoints for SaaS API
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from typing import List
import logging

from ..models.bot_task import BotTask, BotTaskCreate, BotTaskResponse, TaskStatus
from ..models.user import User
from ..services.bot_service import bot_service
from ..config.settings import settings
from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["bot_tasks"])

# In-memory storage for demo (replace with database in production)
tasks_db = {}
task_id_counter = 1

def check_user_task_limit(user: User) -> bool:
    """Check if user has reached their task limit"""
    tier_config = settings.SUBSCRIPTION_TIERS.get(user.subscription_tier)
    if not tier_config:
        return False
    
    user_tasks = [t for t in tasks_db.values() if t.user_id == user.id and t.status != TaskStatus.COMPLETED]
    return len(user_tasks) < tier_config["max_schedules"]

@router.post("", response_model=BotTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: BotTaskCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new bot task"""
    global task_id_counter
    
    # Check task limit
    if not check_user_task_limit(current_user):
        raise HTTPException(
            status_code=403,
            detail=f"Task limit reached for {current_user.subscription_tier} tier"
        )
    
    # Create new task
    new_task = BotTask(
        id=task_id_counter,
        user_id=current_user.id,
        name=task_data.name,
        url=task_data.url,
        target_time=task_data.target_time,
        config=task_data.config,
        status=TaskStatus.SCHEDULED
    )
    
    tasks_db[task_id_counter] = new_task
    task_id_counter += 1
    
    logger.info(f"New task created: {new_task.name} by user {current_user.email}")
    
    return BotTaskResponse(
        id=new_task.id,
        user_id=new_task.user_id,
        name=new_task.name,
        url=new_task.url,
        target_time=new_task.target_time,
        status=new_task.status.value,
        created_at=new_task.created_at,
        updated_at=new_task.updated_at
    )

@router.get("", response_model=List[BotTaskResponse])
async def list_tasks(current_user: User = Depends(get_current_user)):
    """List all tasks for current user"""
    user_tasks = [t for t in tasks_db.values() if t.user_id == current_user.id]
    
    return [
        BotTaskResponse(
            id=task.id,
            user_id=task.user_id,
            name=task.name,
            url=task.url,
            target_time=task.target_time,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in user_tasks
    ]

@router.get("/{task_id}", response_model=BotTaskResponse)
async def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    """Get a specific task"""
    task = tasks_db.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return BotTaskResponse(
        id=task.id,
        user_id=task.user_id,
        name=task.name,
        url=task.url,
        target_time=task.target_time,
        status=task.status.value,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@router.post("/{task_id}/run")
async def run_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Run a bot task"""
    task = tasks_db.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if task.status == TaskStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Task is already running")
    
    # Update task status
    task.status = TaskStatus.RUNNING
    task.started_at = None
    
    # Run task in background
    background_tasks.add_task(
        execute_bot_task,
        task_id,
        task.url,
        task.target_time,
        task.config
    )
    
    logger.info(f"Task {task_id} started by user {current_user.email}")
    
    return {"message": "Task started", "task_id": task_id}

@router.post("/{task_id}/cancel")
async def cancel_task(task_id: int, current_user: User = Depends(get_current_user)):
    """Cancel a running task"""
    task = tasks_db.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if task.status != TaskStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Task is not running")
    
    # Stop the bot
    if bot_service.stop_task(task_id):
        task.status = TaskStatus.CANCELLED
        logger.info(f"Task {task_id} cancelled by user {current_user.email}")
        return {"message": "Task cancelled", "task_id": task_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to cancel task")

@router.delete("/{task_id}")
async def delete_task(task_id: int, current_user: User = Depends(get_current_user)):
    """Delete a task"""
    task = tasks_db.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Cancel task if running
    if task.status == TaskStatus.RUNNING:
        bot_service.stop_task(task_id)
    
    del tasks_db[task_id]
    logger.info(f"Task {task_id} deleted by user {current_user.email}")
    
    return {"message": "Task deleted", "task_id": task_id}

def execute_bot_task(task_id: int, url: str, target_time: str, config: dict):
    """Execute bot task (called in background)"""
    task = tasks_db.get(task_id)
    if not task:
        return
    
    from datetime import datetime
    task.started_at = datetime.now()
    
    try:
        result = bot_service.run_task(task_id, url, target_time, config)
        
        if result["success"]:
            task.status = TaskStatus.COMPLETED
            logger.info(f"Task {task_id} completed successfully")
        else:
            task.status = TaskStatus.FAILED
            task.error_message = result.get("error", "Unknown error")
            logger.error(f"Task {task_id} failed: {task.error_message}")
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        logger.error(f"Task {task_id} failed with exception: {e}")
    finally:
        task.completed_at = datetime.now()
        task.updated_at = datetime.now()
