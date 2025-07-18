"""
策略相关数据模式
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class StrategyBase(BaseModel):
    """策略基础模式"""
    name: str = Field(..., description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    type: str = Field(..., description="策略类型")
    version: str = Field(default="1.0", description="策略版本")

class StrategyCreate(StrategyBase):
    """创建策略模式"""
    config: Dict[str, Any] = Field(..., description="策略配置")
    risk_config: Optional[Dict[str, Any]] = Field(None, description="风险控制配置")

class StrategyUpdate(BaseModel):
    """更新策略模式"""
    name: Optional[str] = Field(None, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    version: Optional[str] = Field(None, description="策略版本")
    config: Optional[Dict[str, Any]] = Field(None, description="策略配置")
    risk_config: Optional[Dict[str, Any]] = Field(None, description="风险控制配置")
    status: Optional[str] = Field(None, description="策略状态")

class StrategyConfig(BaseModel):
    """策略配置模式"""
    # 基础参数
    momentum_period: Optional[int] = Field(20, description="动量周期")
    buy_threshold: Optional[float] = Field(5.0, description="买入阈值")
    sell_threshold: Optional[float] = Field(-3.0, description="卖出阈值")
    max_positions: Optional[int] = Field(10, description="最大持仓数")
    max_position_size: Optional[float] = Field(0.1, description="单股最大仓位")
    min_trade_amount: Optional[float] = Field(10000, description="最小交易金额")
    
    # 风险控制
    stop_loss_rate: Optional[float] = Field(5.0, description="止损比例")
    take_profit_rate: Optional[float] = Field(15.0, description="止盈比例")
    max_drawdown_limit: Optional[float] = Field(10.0, description="最大回撤限制")
    max_holding_days: Optional[int] = Field(30, description="最长持有天数")

class StrategyResponse(StrategyBase):
    """策略响应模式"""
    id: int
    user_id: Optional[int]
    config: Dict[str, Any]
    risk_config: Optional[Dict[str, Any]]
    status: str
    is_active: bool
    total_return: float
    max_drawdown: float
    win_rate: float
    sharpe_ratio: float
    volatility: float
    total_trades: int
    win_trades: int
    running_days: int
    last_run_time: Optional[datetime]
    next_run_time: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class StrategyPerformance(BaseModel):
    """策略性能模式"""
    strategy_id: int
    strategy_name: str
    
    # 收益指标
    total_return: float = Field(..., description="总收益率")
    cumulative_return: float = Field(..., description="累计收益率")
    annualized_return: float = Field(..., description="年化收益率")
    
    # 风险指标
    max_drawdown: float = Field(..., description="最大回撤")
    volatility: float = Field(..., description="波动率")
    sharpe_ratio: float = Field(..., description="夏普比率")
    sortino_ratio: float = Field(..., description="索提诺比率")
    calmar_ratio: float = Field(..., description="卡尔马比率")
    
    # 交易统计
    total_trades: int = Field(..., description="总交易次数")
    win_trades: int = Field(..., description="盈利交易次数")
    win_rate: float = Field(..., description="胜率")
    avg_win: float = Field(..., description="平均盈利")
    avg_loss: float = Field(..., description="平均亏损")
    profit_factor: float = Field(..., description="盈利因子")
    
    # 持仓统计
    avg_holding_period: float = Field(..., description="平均持仓期")
    max_positions: int = Field(..., description="最大持仓数")
    turnover_rate: float = Field(..., description="换手率")
    
    # 基准对比
    benchmark_return: float = Field(..., description="基准收益率")
    alpha: float = Field(..., description="阿尔法")
    beta: float = Field(..., description="贝塔")
    information_ratio: float = Field(..., description="信息比率")
    
    # 运行状态
    status: str = Field(..., description="运行状态")
    running_days: int = Field(..., description="运行天数")
    last_update: datetime = Field(..., description="最后更新时间")

class StrategyTestResult(BaseModel):
    """策略测试结果模式"""
    strategy_id: int
    test_status: str = Field(..., description="测试状态")
    test_message: str = Field(..., description="测试消息")
    
    # 测试结果
    expected_return: Optional[float] = Field(None, description="预期收益率")
    expected_risk: Optional[float] = Field(None, description="预期风险")
    parameter_validity: Dict[str, bool] = Field(..., description="参数有效性")
    
    # 建议
    suggestions: list[str] = Field(default=[], description="优化建议")
    
    test_time: datetime = Field(..., description="测试时间")
