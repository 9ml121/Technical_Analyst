"""
数据服务API路由
提供股票数据获取的REST接口
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from app.services.data_provider_service import DataProviderService
from shared.utils.exceptions import DataSourceError, NetworkError

router = APIRouter(prefix="/api/v1", tags=["数据服务"])

# 初始化数据提供者服务
data_service = DataProviderService()


class StockListResponse(BaseModel):
    """股票列表响应模型"""
    success: bool
    data: List[Dict[str, str]]
    message: str
    timestamp: str
    count: int


class HistoricalDataResponse(BaseModel):
    """历史数据响应模型"""
    success: bool
    data: List[Dict[str, Any]]
    message: str
    timestamp: str
    count: int
    code: str
    start_date: str
    end_date: str


class DataSummaryResponse(BaseModel):
    """数据摘要响应模型"""
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: str


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: str


@router.get("/stocks/list", response_model=StockListResponse)
async def get_stock_list(
    market: str = Query("A", description="市场类型: A( A股), HK(港股)"),
    limit: Optional[int] = Query(None, description="限制返回数量")
):
    """
    获取股票列表

    Args:
        market: 市场类型，A表示A股，HK表示港股
        limit: 限制返回数量，不传则返回全部

    Returns:
        股票列表
    """
    try:
        # 验证市场参数
        if market not in ["A", "HK"]:
            raise HTTPException(status_code=400, detail="不支持的市场类型，支持: A, HK")

        # 获取股票列表
        stocks = data_service.get_stock_list(market)

        # 应用数量限制
        if limit and limit > 0:
            stocks = stocks[:limit]

        return StockListResponse(
            success=True,
            data=stocks,
            message=f"成功获取{market}股票列表",
            timestamp=datetime.now().isoformat(),
            count=len(stocks)
        )

    except DataSourceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except NetworkError as e:
        raise HTTPException(status_code=503, detail=f"数据源暂时不可用: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票列表失败: {str(e)}")


@router.get("/stocks/{code}/history", response_model=HistoricalDataResponse)
async def get_historical_data(
    code: str = Path(..., description="股票代码"),
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)")
):
    """
    获取股票历史数据

    Args:
        code: 股票代码
        start_date: 开始日期，格式：YYYY-MM-DD
        end_date: 结束日期，格式：YYYY-MM-DD

    Returns:
        历史数据列表
    """
    try:
        # 验证股票代码
        if not code or len(code) < 6:
            raise HTTPException(status_code=400, detail="无效的股票代码")

        # 解析日期
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")

        # 验证日期范围
        if start >= end:
            raise HTTPException(status_code=400, detail="开始日期必须早于结束日期")

        # 限制查询范围（最多1年）
        if (end - start).days > 365:
            raise HTTPException(status_code=400, detail="查询范围不能超过1年")

        # 获取历史数据
        data = data_service.get_historical_data(code, start, end)

        return HistoricalDataResponse(
            success=True,
            data=data,
            message=f"成功获取{code}历史数据",
            timestamp=datetime.now().isoformat(),
            count=len(data),
            code=code,
            start_date=start_date,
            end_date=end_date
        )

    except DataSourceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except NetworkError as e:
        raise HTTPException(status_code=503, detail=f"数据源暂时不可用: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")


@router.post("/stocks/batch-history")
async def get_batch_historical_data(
    request: Dict[str, Any]
):
    """
    批量获取股票历史数据

    Args:
        request: 请求体，包含股票代码列表和日期范围
        {
            "codes": ["000001", "600000"],
            "start_date": "2024-01-01",
            "end_date": "2024-01-15"
        }

    Returns:
        批量历史数据
    """
    try:
        # 验证请求参数
        codes = request.get("codes", [])
        start_date = request.get("start_date")
        end_date = request.get("end_date")

        if not codes:
            raise HTTPException(status_code=400, detail="股票代码列表不能为空")

        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="开始日期和结束日期不能为空")

        # 限制批量查询数量
        if len(codes) > 10:
            raise HTTPException(status_code=400, detail="批量查询最多支持10只股票")

        # 解析日期
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")

        # 验证日期范围
        if start >= end:
            raise HTTPException(status_code=400, detail="开始日期必须早于结束日期")

        if (end - start).days > 90:
            raise HTTPException(status_code=400, detail="批量查询日期范围不能超过90天")

        # 批量获取数据
        result = {}
        for code in codes:
            try:
                data = data_service.get_historical_data(code, start, end)
                result[code] = {
                    "success": True,
                    "data": data,
                    "count": len(data)
                }
            except Exception as e:
                result[code] = {
                    "success": False,
                    "error": str(e),
                    "count": 0
                }

        return {
            "success": True,
            "data": result,
            "message": f"批量获取{len(codes)}只股票历史数据完成",
            "timestamp": datetime.now().isoformat(),
            "total_codes": len(codes),
            "successful_codes": len([r for r in result.values() if r["success"]]),
            "failed_codes": len([r for r in result.values() if not r["success"]])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量获取历史数据失败: {str(e)}")


@router.get("/data/summary", response_model=DataSummaryResponse)
async def get_data_summary():
    """
    获取数据摘要信息

    Returns:
        数据摘要统计信息
    """
    try:
        summary = data_service.get_data_summary()

        return DataSummaryResponse(
            success=True,
            data=summary,
            message="成功获取数据摘要",
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据摘要失败: {str(e)}")


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    健康检查

    Returns:
        服务健康状态
    """
    try:
        health = data_service.health_check()

        return HealthCheckResponse(
            success=health["status"] == "healthy",
            data=health,
            message="服务健康检查完成",
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        return HealthCheckResponse(
            success=False,
            data={"error": str(e)},
            message="服务健康检查失败",
            timestamp=datetime.now().isoformat()
        )


@router.get("/stocks/{code}/info")
async def get_stock_info(
    code: str = Path(..., description="股票代码")
):
    """
    获取股票基本信息

    Args:
        code: 股票代码

    Returns:
        股票基本信息
    """
    try:
        # 验证股票代码
        if not code or len(code) < 6:
            raise HTTPException(status_code=400, detail="无效的股票代码")

        # 从数据库获取股票信息
        with data_service.db_path as conn:
            cursor = conn.execute(
                'SELECT code, name, market, list_date FROM stock_info WHERE code = ?',
                (code,)
            )
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail=f"未找到股票{code}的信息")

            return {
                "success": True,
                "data": {
                    "code": row[0],
                    "name": row[1],
                    "market": row[2],
                    "list_date": row[3]
                },
                "message": f"成功获取{code}基本信息",
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票信息失败: {str(e)}")


# 添加路由到主应用
def include_data_routes(app):
    """将数据路由包含到主应用"""
    app.include_router(router)
