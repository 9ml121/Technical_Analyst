"""
性能分析API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/account/{account_id}")
async def get_account_performance(
    account_id: int,
    time_frame: str = "week",
    db: Session = Depends(get_db)
):
    """获取账户表现数据"""
    return {"message": "账户表现API - 开发中"}

@router.get("/strategy/{strategy_id}")
async def get_strategy_performance(
    strategy_id: int,
    time_frame: str = "week",
    db: Session = Depends(get_db)
):
    """获取策略表现数据"""
    return {"message": "策略表现API - 开发中"}
