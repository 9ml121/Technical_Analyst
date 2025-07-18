"""
股票数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StockData(BaseModel):
    """股票数据模型"""
    symbol: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    price: Optional[float] = Field(None, description="当前价格")
    change: Optional[float] = Field(None, description="涨跌幅")
    change_percent: Optional[float] = Field(None, description="涨跌幅百分比")
    volume: Optional[int] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    open: Optional[float] = Field(None, description="开盘价")
    prev_close: Optional[float] = Field(None, description="昨收价")
    timestamp: Optional[datetime] = Field(None, description="时间戳")
    market: Optional[str] = Field(None, description="市场类型")
    source: Optional[str] = Field(None, description="数据源")


class HistoricalData(BaseModel):
    """历史数据模型"""
    symbol: str = Field(..., description="股票代码")
    date: datetime = Field(..., description="日期")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: int = Field(..., description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    market: Optional[str] = Field(None, description="市场类型")
    source: Optional[str] = Field(None, description="数据源")


class StockListResponse(BaseModel):
    """股票列表响应"""
    stocks: List[StockData] = Field(..., description="股票列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="页大小")


class HistoricalDataResponse(BaseModel):
    """历史数据响应"""
    symbol: str = Field(..., description="股票代码")
    data: List[HistoricalData] = Field(..., description="历史数据")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    total_records: int = Field(..., description="总记录数")


class DataSourceInfo(BaseModel):
    """数据源信息"""
    name: str = Field(..., description="数据源名称")
    description: str = Field(..., description="描述")
    supported_markets: List[str] = Field(..., description="支持的市场")
    data_types: List[str] = Field(..., description="数据类型")
    status: str = Field(..., description="状态")


class DataRequest(BaseModel):
    """数据请求模型"""
    symbol: str = Field(..., description="股票代码")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    data_type: str = Field(
        "realtime", description="数据类型: realtime, historical")
    source: Optional[str] = Field(None, description="数据源")
    market: Optional[str] = Field(None, description="市场类型")


class DataResponse(BaseModel):
    """数据响应模型"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="数据")
    message: Optional[str] = Field(None, description="消息")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="时间戳")
