"""
Web Service 配置
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 服务配置
    SERVICE_NAME: str = "web-service"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/technical_analyst"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS配置
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://gateway:8080"
    ]

    # 微服务配置
    GATEWAY_URL: str = "http://gateway:8080"
    CORE_SERVICE_URL: str = "http://core-service:8001"
    DATA_SERVICE_URL: str = "http://data-service:8002"
    STRATEGY_SERVICE_URL: str = "http://strategy-service:8003"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8004"

    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/web-service.log"

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # WebSocket配置
    WEBSOCKET_PING_INTERVAL: int = 20
    WEBSOCKET_PING_TIMEOUT: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()
