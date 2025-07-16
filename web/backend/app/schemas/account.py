"""
账户相关数据模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AccountBase(BaseModel):
    """账户基础模式"""
    name: str = Field(..., description="账户名称")
    description: Optional[str] = Field(None, description="账户描述")

class AccountCreate(AccountBase):
    """创建账户模式"""
    initial_capital: float = Field(..., gt=0, description="初始资金")
    strategy_id: Optional[int] = Field(None, description="关联策略ID")
    config: Optional[Dict[str, Any]] = Field(None, description="账户配置")

class AccountUpdate(BaseModel):
    """更新账户模式"""
    name: Optional[str] = Field(None, description="账户名称")
    description: Optional[str] = Field(None, description="账户描述")
    status: Optional[str] = Field(None, description="账户状态")
    config: Optional[Dict[str, Any]] = Field(None, description="账户配置")

class AccountResponse(AccountBase):
    """账户响应模式"""
    id: int
    initial_capital: float
    current_capital: float
    available_capital: float
    frozen_capital: float
    total_market_value: float
    total_asset: float
    total_profit: float
    total_return_rate: float
    today_profit: float
    today_return_rate: float
    max_drawdown: float
    win_rate: float
    sharpe_ratio: float
    total_trades: int
    win_trades: int
    strategy_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AccountSummary(BaseModel):
    """账户概览模式 - 用于模拟实盘交易页面"""
    account_id: int = Field(..., description="账户ID")
    account_name: str = Field(..., description="账户名称")

    # 资产信息
    total_asset: float = Field(..., description="总资产")
    total_profit: float = Field(..., description="累计盈亏")
    total_return_rate: float = Field(..., description="累计收益率")
    today_profit: float = Field(..., description="今日盈亏")
    today_return_rate: float = Field(..., description="今日收益率")

    # 持仓信息
    position_count: int = Field(..., description="持仓数量")
    position_ratio: float = Field(..., description="仓位比例")

    # 交易统计
    total_trades: int = Field(..., description="总交易次数")
    win_trades: int = Field(..., description="盈利交易次数")
    win_rate: float = Field(..., description="胜率")

    # 风险指标
    max_drawdown: float = Field(..., description="最大回撤")
    sharpe_ratio: float = Field(..., description="夏普比率")

    # 状态信息
    status: str = Field(..., description="账户状态")
    last_update: datetime = Field(..., description="最后更新时间")

class PositionBase(BaseModel):
    """持仓基础模式"""
    symbol: str = Field(..., description="股票代码")
    symbol_name: Optional[str] = Field(None, description="股票名称")

class PositionResponse(PositionBase):
    """持仓响应模式"""
    id: int
    account_id: int
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_rate: float
    first_buy_date: Optional[datetime]
    last_trade_date: Optional[datetime]
    holding_days: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
