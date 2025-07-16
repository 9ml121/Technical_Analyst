"""
市场数据相关数据模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class MarketIndexResponse(BaseModel):
    """市场指数响应模式"""
    id: int
    code: str
    name: str
    current_value: float
    change_value: float
    change_percent: float
    volume: Optional[int]
    amount: Optional[float]
    trade_date: date
    timestamp: datetime
    
    class Config:
        from_attributes = True

class MarketStatsResponse(BaseModel):
    """市场统计响应模式"""
    id: int
    trade_date: date
    rise_count: int
    fall_count: int
    flat_count: int
    limit_up_count: int
    limit_down_count: int
    total_volume: int
    total_amount: float
    market_sentiment: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class StockQuoteResponse(BaseModel):
    """股票行情响应模式"""
    id: int
    symbol: str
    symbol_name: Optional[str]
    current_price: float
    change_value: float
    change_percent: float
    volume: int
    amount: float
    trade_date: date
    timestamp: datetime
    
    class Config:
        from_attributes = True

class MarketOverview(BaseModel):
    """市场概览模式"""
    indices: List[MarketIndexResponse]
    stats: MarketStatsResponse
    market_status: str
    update_time: datetime

class BenchmarkComparison(BaseModel):
    """基准对比模式"""
    benchmark_code: str
    benchmark_name: str
    account_return: float
    benchmark_return: float
    excess_return: float
    comparison_period: str
