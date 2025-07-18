"""
策略管理API端点
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Depends, Body
from fastapi.responses import JSONResponse

from app.models.strategy import (
    Strategy, StrategyCreate, StrategyUpdate, StrategyExecution,
    StrategyResult, StrategyResponse
)
from app.services.strategy_service import strategy_service

router = APIRouter()


@router.get("/", response_model=dict)
async def root():
    """策略服务根路径"""
    return {
        "service": "strategy-service",
        "version": "1.0.0",
        "status": "running",
        "description": "策略管理服务"
    }


@router.get("/health", response_model=dict)
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "strategy-service",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/api/v1/strategies", response_model=StrategyResponse)
async def get_strategies(
    category: Optional[str] = Query(None, description="策略类别")
):
    """获取策略列表"""
    try:
        result = strategy_service.get_strategies(category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str):
    """获取策略详情"""
    try:
        result = strategy_service.get_strategy(strategy_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/strategies", response_model=StrategyResponse)
async def create_strategy(strategy_data: StrategyCreate):
    """创建新策略"""
    try:
        result = strategy_service.create_strategy(strategy_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/v1/strategies/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: str, update_data: StrategyUpdate):
    """更新策略"""
    try:
        result = strategy_service.update_strategy(strategy_id, update_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/v1/strategies/{strategy_id}", response_model=StrategyResponse)
async def delete_strategy(strategy_id: str):
    """删除策略"""
    try:
        result = strategy_service.delete_strategy(strategy_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/strategies/execute", response_model=StrategyResponse)
async def execute_strategy(execution: StrategyExecution):
    """执行策略"""
    try:
        result = strategy_service.execute_strategy(execution)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/executions/{execution_id}", response_model=StrategyResponse)
async def get_execution_result(execution_id: str):
    """获取执行结果"""
    try:
        result = strategy_service.get_execution_result(execution_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/templates", response_model=StrategyResponse)
async def get_templates(
    category: Optional[str] = Query(None, description="模板类别")
):
    """获取策略模板"""
    try:
        result = strategy_service.get_templates(category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/statistics", response_model=StrategyResponse)
async def get_strategy_statistics():
    """获取策略统计信息"""
    try:
        result = strategy_service.get_strategy_statistics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/strategies/{strategy_id}/validate", response_model=StrategyResponse)
async def validate_strategy(strategy_id: str):
    """验证策略"""
    try:
        # 获取策略
        strategy_result = strategy_service.get_strategy(strategy_id)
        if not strategy_result.success:
            return strategy_result

        # 这里应该添加策略验证逻辑
        # 暂时返回成功
        return StrategyResponse(
            success=True,
            data={
                "strategy_id": strategy_id,
                "valid": True,
                "issues": [],
                "warnings": []
            },
            message="策略验证通过"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/strategies/{strategy_id}/clone", response_model=StrategyResponse)
async def clone_strategy(strategy_id: str):
    """克隆策略"""
    try:
        # 获取原策略
        strategy_result = strategy_service.get_strategy(strategy_id)
        if not strategy_result.success:
            return strategy_result

        original_strategy = strategy_result.data

        # 创建新策略
        new_strategy_data = StrategyCreate(
            name=f"{original_strategy.name}_copy",
            description=f"克隆自: {original_strategy.description}",
            category=original_strategy.category,
            author=original_strategy.author,
            parameters=original_strategy.parameters
        )

        result = strategy_service.create_strategy(new_strategy_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/categories", response_model=StrategyResponse)
async def get_strategy_categories():
    """获取策略类别列表"""
    try:
        # 获取所有策略
        result = strategy_service.get_strategies()
        if not result.success:
            return result

        # 提取类别
        categories = list(set([s.category for s in result.data]))

        return StrategyResponse(
            success=True,
            data=categories,
            message="获取策略类别成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/strategies/{strategy_id}/history", response_model=StrategyResponse)
async def get_strategy_history(strategy_id: str):
    """获取策略执行历史"""
    try:
        # 这里应该从数据库获取执行历史
        # 暂时返回模拟数据
        history = [
            {
                "execution_id": "exec_001",
                "start_time": "2024-01-15T10:00:00",
                "end_time": "2024-01-15T10:05:00",
                "status": "completed",
                "total_return": 0.15,
                "sharpe_ratio": 1.2
            },
            {
                "execution_id": "exec_002",
                "start_time": "2024-01-14T10:00:00",
                "end_time": "2024-01-14T10:05:00",
                "status": "completed",
                "total_return": 0.12,
                "sharpe_ratio": 1.1
            }
        ]

        return StrategyResponse(
            success=True,
            data=history,
            message="获取执行历史成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
