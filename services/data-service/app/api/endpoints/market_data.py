"""
市场数据API端点
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models.stock_data import (
    StockData, HistoricalData, DataResponse,
    StockListResponse, HistoricalDataResponse, DataSourceInfo,
    DataRequest
)
from app.services.market_data_service import market_data_service

router = APIRouter()


@router.get("/", response_model=dict)
async def root():
    """数据服务根路径"""
    return {
        "service": "data-service",
        "version": "1.0.0",
        "status": "running",
        "description": "市场数据获取服务"
    }


@router.get("/health", response_model=dict)
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "data-service",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/stocks/{symbol}", response_model=DataResponse)
async def get_stock_data(
    symbol: str,
    source: str = Query("eastmoney", description="数据源")
):
    """获取股票实时数据"""
    try:
        result = market_data_service.get_stock_data(symbol, source)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/{symbol}/historical", response_model=DataResponse)
async def get_historical_data(
    symbol: str,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    source: str = Query("eastmoney", description="数据源")
):
    """获取股票历史数据"""
    try:
        # 解析日期
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        result = market_data_service.get_historical_data(
            symbol, start_dt, end_dt, source
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks", response_model=DataResponse)
async def get_stock_list(
    market: str = Query("CN", description="市场类型"),
    source: str = Query("eastmoney", description="数据源")
):
    """获取股票列表"""
    try:
        result = market_data_service.get_stock_list(market, source)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=DataResponse)
async def search_stocks(
    keyword: str = Query(..., description="搜索关键词"),
    source: str = Query("eastmoney", description="数据源")
):
    """搜索股票"""
    try:
        result = market_data_service.search_stocks(keyword, source)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=DataResponse)
async def get_data_sources():
    """获取可用数据源信息"""
    try:
        result = market_data_service.get_data_sources()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data", response_model=DataResponse)
async def get_data(request: DataRequest):
    """通用数据获取接口"""
    try:
        if request.data_type == "realtime":
            result = market_data_service.get_stock_data(
                request.symbol,
                request.source or "eastmoney"
            )
        elif request.data_type == "historical":
            if not request.start_date or not request.end_date:
                raise HTTPException(
                    status_code=400,
                    detail="历史数据需要指定开始和结束日期"
                )
            result = market_data_service.get_historical_data(
                request.symbol,
                request.start_date,
                request.end_date,
                request.source or "eastmoney"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="不支持的数据类型，支持: realtime, historical"
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/markets/{market}/stocks", response_model=DataResponse)
async def get_market_stocks(
    market: str,
    source: str = Query("eastmoney", description="数据源")
):
    """获取指定市场的股票列表"""
    try:
        result = market_data_service.get_stock_list(market, source)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/{symbol}/summary", response_model=DataResponse)
async def get_stock_summary(
    symbol: str,
    source: str = Query("eastmoney", description="数据源")
):
    """获取股票摘要信息"""
    try:
        # 获取实时数据
        realtime_result = market_data_service.get_stock_data(symbol, source)

        if not realtime_result.success:
            return realtime_result

        # 获取最近30天的历史数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        historical_result = market_data_service.get_historical_data(
            symbol, start_date, end_date, source
        )

        # 构建摘要信息
        summary = {
            "symbol": symbol,
            "realtime": realtime_result.data,
            "historical_summary": {
                "period": "30天",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "data_count": len(historical_result.data.data) if historical_result.success else 0
            }
        }

        return DataResponse(
            success=True,
            data=summary,
            message="获取摘要成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
