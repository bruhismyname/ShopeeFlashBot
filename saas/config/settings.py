"""
Configuration settings for ShopeeFlashBot SaaS platform
"""
import os
from typing import Dict, Any

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shopee_saas.db")
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_PREFIX = "/api/v1"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Bot Configuration
    MAX_CONCURRENT_BOTS = int(os.getenv("MAX_CONCURRENT_BOTS", "10"))
    BOT_TIMEOUT = int(os.getenv("BOT_TIMEOUT", "300"))
    
    # Subscription Tiers
    SUBSCRIPTION_TIERS: Dict[str, Dict[str, Any]] = {
        "free": {
            "max_bots": 1,
            "max_schedules": 5,
            "priority": 3,
            "price": 0
        },
        "basic": {
            "max_bots": 3,
            "max_schedules": 20,
            "priority": 2,
            "price": 9.99
        },
        "premium": {
            "max_bots": 10,
            "max_schedules": 100,
            "priority": 1,
            "price": 29.99
        }
    }
    
    # Redis/Queue
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Email (for notifications)
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
settings = Settings()
