"""
数据服务配置
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 服务配置
    service_name: str = "data-service"
    version: str = "1.0.0"
    debug: bool = False

    # 数据库配置
    database_url: Optional[str] = None

    # Redis配置
    redis_url: Optional[str] = None

    # 数据源配置
    default_data_source: str = "eastmoney"
    tushare_token: Optional[str] = None

    # API配置
    api_prefix: str = "/api/v1"
    cors_origins: list = ["*"]

    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 缓存配置
    cache_ttl: int = 300  # 5分钟
    max_cache_size: int = 1000

    # 请求配置
    request_timeout: int = 30
    max_retries: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
