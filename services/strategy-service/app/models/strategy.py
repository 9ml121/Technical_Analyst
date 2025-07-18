"""
策略管理模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Strategy(BaseModel):
    """策略模型"""
    id: Optional[str] = Field(None, description="策略ID")
    name: str = Field(..., description="策略名称")
    description: str = Field(..., description="策略描述")
    category: str = Field(..., description="策略类别")
    author: str = Field(..., description="策略作者")
    version: str = Field("1.0.0", description="策略版本")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="策略参数")
    status: str = Field("active", description="策略状态")
    created_at: datetime = Field(
        default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(
        default_factory=datetime.now, description="更新时间")


class StrategyCreate(BaseModel):
    """创建策略请求"""
    name: str = Field(..., description="策略名称")
    description: str = Field(..., description="策略描述")
    category: str = Field(..., description="策略类别")
    author: str = Field(..., description="策略作者")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="策略参数")


class StrategyUpdate(BaseModel):
    """更新策略请求"""
    name: Optional[str] = Field(None, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    category: Optional[str] = Field(None, description="策略类别")
    parameters: Optional[Dict[str, Any]] = Field(None, description="策略参数")
    status: Optional[str] = Field(None, description="策略状态")


class StrategyExecution(BaseModel):
    """策略执行模型"""
    strategy_id: str = Field(..., description="策略ID")
    symbols: List[str] = Field(..., description="股票代码列表")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="执行参数")


class StrategyResult(BaseModel):
    """策略执行结果"""
    execution_id: str = Field(..., description="执行ID")
    strategy_id: str = Field(..., description="策略ID")
    status: str = Field(..., description="执行状态")
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    results: Optional[Dict[str, Any]] = Field(None, description="执行结果")
    error_message: Optional[str] = Field(None, description="错误信息")


class StrategyTemplate(BaseModel):
    """策略模板"""
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    category: str = Field(..., description="模板类别")
    code_template: str = Field(..., description="代码模板")
    parameters_schema: Dict[str, Any] = Field(..., description="参数模式")


class StrategyResponse(BaseModel):
    """策略服务响应模型"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="数据")
    message: Optional[str] = Field(None, description="消息")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="时间戳")
