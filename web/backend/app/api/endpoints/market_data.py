"""
市场数据API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import logging

from app.core.database import get_db
from app.models.market_data import MarketIndex, MarketStats, StockQuote
from app.services.market_data_service import MarketDataService
from app.schemas.market_data import (
    MarketIndexResponse, MarketStatsResponse, StockQuoteResponse,
    MarketOverview, BenchmarkComparison
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/indices", response_model=List[MarketIndexResponse])
async def get_market_indices(
    codes: Optional[str] = None,  # 逗号分隔的指数代码
    db: Session = Depends(get_db)
):
    """获取市场指数数据"""
    try:
        query = db.query(MarketIndex)
        
        if codes:
            code_list = [code.strip() for code in codes.split(",")]
            query = query.filter(MarketIndex.code.in_(code_list))
        
        # 获取最新数据
        indices = query.filter(
            MarketIndex.trade_date == date.today()
        ).all()
        
        # 如果今天没有数据，获取最近的数据
        if not indices:
            indices = query.order_by(
                MarketIndex.trade_date.desc()
            ).limit(10).all()
        
        return indices
    except Exception as e:
        logger.error(f"获取市场指数失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取市场指数失败"
        )

@router.get("/stats", response_model=MarketStatsResponse)
async def get_market_stats(
    trade_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取市场统计数据"""
    try:
        if not trade_date:
            trade_date = date.today()
        
        stats = db.query(MarketStats).filter(
            MarketStats.trade_date == trade_date
        ).first()
        
        if not stats:
            # 如果没有指定日期的数据，获取最新数据
            stats = db.query(MarketStats).order_by(
                MarketStats.trade_date.desc()
            ).first()
        
        if not stats:
            # 如果没有任何数据，返回模拟数据
            stats = MarketStats(
                trade_date=trade_date,
                rise_count=1856,
                fall_count=1234,
                flat_count=456,
                limit_up_count=23,
                limit_down_count=8,
                total_volume=2456000000,
                total_amount=245600000000.0,
                active_stocks=3546,
                suspended_stocks=123
            )
            stats.calculate_sentiment()
        
        return stats
    except Exception as e:
        logger.error(f"获取市场统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取市场统计失败"
        )

@router.get("/overview", response_model=MarketOverview)
async def get_market_overview(
    db: Session = Depends(get_db)
):
    """获取市场概览"""
    try:
        market_service = MarketDataService(db)
        overview = await market_service.get_market_overview()
        return overview
    except Exception as e:
        logger.error(f"获取市场概览失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取市场概览失败"
        )

@router.get("/quotes/{symbol}", response_model=StockQuoteResponse)
async def get_stock_quote(
    symbol: str,
    db: Session = Depends(get_db)
):
    """获取股票行情"""
    try:
        quote = db.query(StockQuote).filter(
            StockQuote.symbol == symbol,
            StockQuote.trade_date == date.today()
        ).first()
        
        if not quote:
            # 如果没有今天的数据，获取最新数据
            quote = db.query(StockQuote).filter(
                StockQuote.symbol == symbol
            ).order_by(StockQuote.trade_date.desc()).first()
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="股票行情不存在"
            )
        
        return quote
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票行情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取股票行情失败"
        )

@router.get("/quotes", response_model=List[StockQuoteResponse])
async def get_stock_quotes(
    symbols: str,  # 逗号分隔的股票代码
    db: Session = Depends(get_db)
):
    """批量获取股票行情"""
    try:
        symbol_list = [symbol.strip() for symbol in symbols.split(",")]
        
        quotes = db.query(StockQuote).filter(
            StockQuote.symbol.in_(symbol_list),
            StockQuote.trade_date == date.today()
        ).all()
        
        # 如果今天没有数据，获取最新数据
        if not quotes:
            quotes = db.query(StockQuote).filter(
                StockQuote.symbol.in_(symbol_list)
            ).order_by(StockQuote.trade_date.desc()).limit(len(symbol_list)).all()
        
        return quotes
    except Exception as e:
        logger.error(f"批量获取股票行情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量获取股票行情失败"
        )

@router.get("/benchmark/{benchmark_code}", response_model=BenchmarkComparison)
async def get_benchmark_comparison(
    benchmark_code: str,
    account_id: Optional[int] = None,
    strategy_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取基准对比数据"""
    try:
        market_service = MarketDataService(db)
        comparison = await market_service.get_benchmark_comparison(
            benchmark_code, account_id, strategy_id
        )
        return comparison
    except Exception as e:
        logger.error(f"获取基准对比失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取基准对比失败"
        )

@router.post("/update")
async def update_market_data(
    db: Session = Depends(get_db)
):
    """手动更新市场数据"""
    try:
        market_service = MarketDataService(db)
        await market_service.update_market_data()
        return {"message": "市场数据更新成功"}
    except Exception as e:
        logger.error(f"更新市场数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新市场数据失败"
        )

@router.get("/realtime/indices")
async def get_realtime_indices():
    """获取实时指数数据（模拟）"""
    try:
        # 模拟实时数据
        realtime_data = {
            "timestamp": datetime.now().isoformat(),
            "indices": [
                {
                    "code": "000001",
                    "name": "上证指数",
                    "current": 2956.85 + (hash(str(datetime.now().second)) % 20 - 10) * 0.1,
                    "change": 15.23 + (hash(str(datetime.now().second)) % 10 - 5) * 0.1,
                    "change_percent": 0.52 + (hash(str(datetime.now().second)) % 10 - 5) * 0.01
                },
                {
                    "code": "000300",
                    "name": "沪深300",
                    "current": 3456.78 + (hash(str(datetime.now().second)) % 20 - 10) * 0.1,
                    "change": 23.45 + (hash(str(datetime.now().second)) % 10 - 5) * 0.1,
                    "change_percent": 0.68 + (hash(str(datetime.now().second)) % 10 - 5) * 0.01
                },
                {
                    "code": "399001",
                    "name": "深证成指",
                    "current": 9234.56 + (hash(str(datetime.now().second)) % 20 - 10) * 0.1,
                    "change": -12.34 + (hash(str(datetime.now().second)) % 10 - 5) * 0.1,
                    "change_percent": -0.13 + (hash(str(datetime.now().second)) % 10 - 5) * 0.01
                },
                {
                    "code": "399006",
                    "name": "创业板指",
                    "current": 2123.45 + (hash(str(datetime.now().second)) % 20 - 10) * 0.1,
                    "change": 8.76 + (hash(str(datetime.now().second)) % 10 - 5) * 0.1,
                    "change_percent": 0.41 + (hash(str(datetime.now().second)) % 10 - 5) * 0.01
                }
            ]
        }
        return realtime_data
    except Exception as e:
        logger.error(f"获取实时指数数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取实时指数数据失败"
        )
