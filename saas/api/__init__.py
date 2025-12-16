"""
API module initialization
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .bot_tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(tasks_router)

__all__ = ["api_router"]
