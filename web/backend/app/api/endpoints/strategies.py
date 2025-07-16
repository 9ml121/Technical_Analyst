"""
策略管理API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.strategy import Strategy
from app.services.strategy_service import StrategyService
from app.schemas.strategy import (
    StrategyResponse, StrategyCreate, StrategyUpdate,
    StrategyConfig, StrategyPerformance
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取策略列表"""
    try:
        query = db.query(Strategy)
        
        if status:
            query = query.filter(Strategy.status == status)
        
        if type:
            query = query.filter(Strategy.type == type)
        
        strategies = query.offset(skip).limit(limit).all()
        return strategies
    except Exception as e:
        logger.error(f"获取策略列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取策略列表失败"
        )

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """获取单个策略信息"""
    try:
        strategy = db.query(Strategy).filter(
            Strategy.id == strategy_id
        ).first()
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="策略不存在"
            )
        
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取策略信息失败"
        )

@router.get("/{strategy_id}/performance", response_model=StrategyPerformance)
async def get_strategy_performance(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """获取策略性能指标"""
    try:
        strategy_service = StrategyService(db)
        performance = await strategy_service.get_strategy_performance(strategy_id)
        return performance
    except Exception as e:
        logger.error(f"获取策略性能失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取策略性能失败"
        )

@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    db: Session = Depends(get_db)
):
    """创建新策略"""
    try:
        strategy_service = StrategyService(db)
        new_strategy = await strategy_service.create_strategy(strategy)
        return new_strategy
    except Exception as e:
        logger.error(f"创建策略失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建策略失败"
        )

@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdate,
    db: Session = Depends(get_db)
):
    """更新策略信息"""
    try:
        strategy_service = StrategyService(db)
        updated_strategy = await strategy_service.update_strategy(
            strategy_id, strategy_update
        )
        return updated_strategy
    except Exception as e:
        logger.error(f"更新策略失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新策略失败"
        )

@router.post("/{strategy_id}/start")
async def start_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """启动策略"""
    try:
        strategy_service = StrategyService(db)
        await strategy_service.start_strategy(strategy_id)
        return {"message": "策略启动成功"}
    except Exception as e:
        logger.error(f"启动策略失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="启动策略失败"
        )

@router.post("/{strategy_id}/stop")
async def stop_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """停止策略"""
    try:
        strategy_service = StrategyService(db)
        await strategy_service.stop_strategy(strategy_id)
        return {"message": "策略停止成功"}
    except Exception as e:
        logger.error(f"停止策略失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="停止策略失败"
        )

@router.post("/{strategy_id}/pause")
async def pause_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """暂停策略"""
    try:
        strategy_service = StrategyService(db)
        await strategy_service.pause_strategy(strategy_id)
        return {"message": "策略暂停成功"}
    except Exception as e:
        logger.error(f"暂停策略失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="暂停策略失败"
        )

@router.put("/{strategy_id}/config")
async def update_strategy_config(
    strategy_id: int,
    config: StrategyConfig,
    db: Session = Depends(get_db)
):
    """更新策略配置"""
    try:
        strategy_service = StrategyService(db)
        await strategy_service.update_strategy_config(strategy_id, config)
        return {"message": "策略配置更新成功"}
    except Exception as e:
        logger.error(f"更新策略配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新策略配置失败"
        )

@router.post("/{strategy_id}/test")
async def test_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """测试策略参数"""
    try:
        strategy_service = StrategyService(db)
        test_result = await strategy_service.test_strategy(strategy_id)
        return test_result
    except Exception as e:
        logger.error(f"测试策略失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="测试策略失败"
        )

@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """删除策略"""
    try:
        strategy = db.query(Strategy).filter(
            Strategy.id == strategy_id
        ).first()
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="策略不存在"
            )
        
        # 检查策略是否正在运行
        if strategy.status == "running":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法删除正在运行的策略，请先停止策略"
            )
        
        db.delete(strategy)
        db.commit()
        
        return {"message": "策略删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除策略失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除策略失败"
        )
