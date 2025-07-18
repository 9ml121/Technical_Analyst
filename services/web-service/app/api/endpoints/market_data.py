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
from app.services.real_market_data import real_market_service
from app.schemas.market_data import (
    MarketIndexResponse, MarketStatsResponse, StockQuoteResponse,
    MarketOverview, BenchmarkComparison
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/realtime/indices")
async def get_realtime_indices():
    """获取实时市场指数数据"""
    try:
        # 获取真实的市场数据
        data = await real_market_service.get_market_indices()
        return data
    except Exception as e:
        logger.error(f"获取实时指数数据失败: {e}")
        # 如果获取失败，返回备用数据
        return real_market_service._get_fallback_data()

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

@router.get("/realtime/quotes")
async def get_realtime_quotes(
    symbols: str,  # 逗号分隔的股票代码
    db: Session = Depends(get_db)
):
    """获取实时股票行情（模拟）"""
    try:
        symbol_list = [symbol.strip() for symbol in symbols.split(",")]
        realtime_quotes = []

        for symbol in symbol_list:
            # 模拟实时股票数据
            base_price = 10.0 + (hash(symbol) % 100)
            current_price = base_price + (hash(str(datetime.now().second) + symbol) % 20 - 10) * 0.01
            change = current_price - base_price
            change_percent = (change / base_price) * 100

            quote = {
                "symbol": symbol,
                "name": f"股票{symbol}",
                "current_price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": (hash(symbol) % 1000000) * 100,
                "amount": current_price * ((hash(symbol) % 1000000) * 100),
                "timestamp": datetime.now().isoformat()
            }
            realtime_quotes.append(quote)

        return {
            "timestamp": datetime.now().isoformat(),
            "quotes": realtime_quotes
        }
    except Exception as e:
        logger.error(f"获取实时股票行情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取实时股票行情失败"
        )
