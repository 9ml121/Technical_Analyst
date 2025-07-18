"""
量化分析API端点
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Depends, Body
from fastapi.responses import JSONResponse

from app.models.analysis import (
    AnalysisRequest, AnalysisResult, CoreResponse,
    BacktestRequest, BacktestResult, StrategyInfo
)
from app.services.analysis_service import analysis_service

router = APIRouter()


@router.get("/", response_model=dict)
async def root():
    """核心服务根路径"""
    return {
        "service": "core-service",
        "version": "1.0.0",
        "status": "running",
        "description": "量化分析核心服务"
    }


@router.get("/health", response_model=dict)
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "core-service",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/analysis/{symbol}", response_model=CoreResponse)
async def analyze_stock(
    symbol: str,
    analysis_type: str = Query(
        "technical", description="分析类型: technical, fundamental, sentiment"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)")
):
    """分析股票"""
    try:
        # 解析日期
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        request = AnalysisRequest(
            symbol=symbol,
            analysis_type=analysis_type,
            start_date=start_dt,
            end_date=end_dt
        )

        result = analysis_service.analyze_stock(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analysis", response_model=CoreResponse)
async def analyze_stock_post(request: AnalysisRequest):
    """分析股票 (POST)"""
    try:
        result = analysis_service.analyze_stock(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{symbol}/summary", response_model=CoreResponse)
async def get_analysis_summary(symbol: str):
    """获取股票分析摘要"""
    try:
        result = analysis_service.get_analysis_summary(symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest", response_model=CoreResponse)
async def run_backtest(request: BacktestRequest):
    """运行回测"""
    try:
        result = analysis_service.run_backtest(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies", response_model=CoreResponse)
async def get_strategies():
    """获取可用策略列表"""
    try:
        result = analysis_service.get_strategies()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies/{strategy_name}", response_model=CoreResponse)
async def get_strategy_info(strategy_name: str):
    """获取策略详细信息"""
    try:
        # 获取所有策略
        result = analysis_service.get_strategies()
        if not result.success:
            return result

        # 查找指定策略
        for strategy in result.data:
            if strategy.name == strategy_name:
                return CoreResponse(
                    success=True,
                    data=strategy,
                    message="获取策略信息成功"
                )

        return CoreResponse(
            success=False,
            message=f"未找到策略: {strategy_name}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators", response_model=CoreResponse)
async def get_available_indicators():
    """获取可用技术指标列表"""
    try:
        indicators = [
            {
                "name": "MA",
                "description": "移动平均线",
                "parameters": ["period"],
                "category": "trend"
            },
            {
                "name": "RSI",
                "description": "相对强弱指数",
                "parameters": ["period"],
                "category": "momentum"
            },
            {
                "name": "MACD",
                "description": "MACD指标",
                "parameters": ["fast_period", "slow_period", "signal_period"],
                "category": "trend"
            },
            {
                "name": "BB",
                "description": "布林带",
                "parameters": ["period", "std_dev"],
                "category": "volatility"
            },
            {
                "name": "KDJ",
                "description": "KDJ指标",
                "parameters": ["k_period", "d_period"],
                "category": "momentum"
            }
        ]

        return CoreResponse(
            success=True,
            data=indicators,
            message="获取技术指标列表成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{symbol}/technical", response_model=CoreResponse)
async def technical_analysis(symbol: str):
    """技术分析"""
    try:
        request = AnalysisRequest(
            symbol=symbol,
            analysis_type="technical"
        )
        result = analysis_service.analyze_stock(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{symbol}/fundamental", response_model=CoreResponse)
async def fundamental_analysis(symbol: str):
    """基本面分析"""
    try:
        request = AnalysisRequest(
            symbol=symbol,
            analysis_type="fundamental"
        )
        result = analysis_service.analyze_stock(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{symbol}/sentiment", response_model=CoreResponse)
async def sentiment_analysis(symbol: str):
    """情感分析"""
    try:
        request = AnalysisRequest(
            symbol=symbol,
            analysis_type="sentiment"
        )
        result = analysis_service.analyze_stock(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance", response_model=CoreResponse)
async def get_performance_metrics():
    """获取性能指标"""
    try:
        metrics = {
            "service": "core-service",
            "uptime": "99.9%",
            "response_time": "150ms",
            "requests_per_second": 100,
            "active_connections": 25,
            "memory_usage": "512MB",
            "cpu_usage": "15%"
        }

        return CoreResponse(
            success=True,
            data=metrics,
            message="获取性能指标成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
