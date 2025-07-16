"""
配置管理
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "Technical_Analyst Web Interface"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./technical_analyst_web.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 量化系统配置
    QUANT_SYSTEM_PATH: str = "../.."  # 指向量化系统根目录
    DEFAULT_INITIAL_CAPITAL: float = 100000.0  # 默认10万本金
    
    # 数据源配置
    MARKET_DATA_UPDATE_INTERVAL: int = 1  # 秒
    ENABLE_REAL_TRADING: bool = False  # 是否启用真实交易
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/web_interface.log"
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()

# 确保必要的目录存在
os.makedirs("logs", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)
