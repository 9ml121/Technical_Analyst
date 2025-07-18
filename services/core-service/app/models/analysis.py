"""
量化分析模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    symbol: str = Field(..., description="股票代码")
    analysis_type: str = Field(...,
                               description="分析类型: technical, fundamental, sentiment")
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="分析参数")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")


class TechnicalIndicator(BaseModel):
    """技术指标模型"""
    name: str = Field(..., description="指标名称")
    value: float = Field(..., description="指标值")
    signal: str = Field(..., description="信号: buy, sell, hold")
    description: Optional[str] = Field(None, description="描述")


class AnalysisResult(BaseModel):
    """分析结果模型"""
    symbol: str = Field(..., description="股票代码")
    analysis_type: str = Field(..., description="分析类型")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="分析时间")
    indicators: List[TechnicalIndicator] = Field(..., description="技术指标")
    summary: str = Field(..., description="分析摘要")
    recommendation: str = Field(..., description="投资建议")
    confidence: float = Field(..., description="置信度 (0-1)")
    risk_level: str = Field(..., description="风险等级: low, medium, high")


class BacktestRequest(BaseModel):
    """回测请求模型"""
    strategy_name: str = Field(..., description="策略名称")
    symbols: List[str] = Field(..., description="股票代码列表")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    initial_capital: float = Field(1000000.0, description="初始资金")
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="策略参数")


class BacktestResult(BaseModel):
    """回测结果模型"""
    strategy_name: str = Field(..., description="策略名称")
    symbols: List[str] = Field(..., description="股票代码列表")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    initial_capital: float = Field(..., description="初始资金")
    final_capital: float = Field(..., description="最终资金")
    total_return: float = Field(..., description="总收益率")
    annual_return: float = Field(..., description="年化收益率")
    max_drawdown: float = Field(..., description="最大回撤")
    sharpe_ratio: float = Field(..., description="夏普比率")
    win_rate: float = Field(..., description="胜率")
    total_trades: int = Field(..., description="总交易次数")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="回测时间")


class StrategyInfo(BaseModel):
    """策略信息模型"""
    name: str = Field(..., description="策略名称")
    description: str = Field(..., description="策略描述")
    category: str = Field(..., description="策略类别")
    parameters: Dict[str, Any] = Field(..., description="策略参数")
    status: str = Field(..., description="策略状态")


class CoreResponse(BaseModel):
    """核心服务响应模型"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="数据")
    message: Optional[str] = Field(None, description="消息")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="时间戳")
