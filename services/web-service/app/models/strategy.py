"""
策略模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Strategy(Base):
    """策略表"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 暂时允许为空
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50), nullable=False)  # momentum, ml, custom等
    version = Column(String(20), default="1.0")
    
    # 策略配置
    config = Column(JSON, nullable=False)  # 策略参数配置
    risk_config = Column(JSON)  # 风险控制配置
    
    # 运行状态
    status = Column(String(20), default="stopped")  # running, stopped, paused
    is_active = Column(Boolean, default=True)
    
    # 性能指标
    total_return = Column(Float, default=0)  # 累计收益率
    max_drawdown = Column(Float, default=0)  # 最大回撤
    win_rate = Column(Float, default=0)  # 胜率
    sharpe_ratio = Column(Float, default=0)  # 夏普比率
    volatility = Column(Float, default=0)  # 波动率
    
    # 运行统计
    total_trades = Column(Integer, default=0)  # 总交易次数
    win_trades = Column(Integer, default=0)  # 盈利交易次数
    running_days = Column(Integer, default=0)  # 运行天数
    
    # 时间信息
    last_run_time = Column(DateTime(timezone=True))  # 最后运行时间
    next_run_time = Column(DateTime(timezone=True))  # 下次运行时间
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="strategies")
    accounts = relationship("SimulatedAccount", back_populates="strategy")
    signals = relationship("TradingSignal", back_populates="strategy")
    performance_records = relationship("StrategyPerformance", back_populates="strategy")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}', type='{self.type}', status='{self.status}')>"
    
    @property
    def is_running(self):
        """是否正在运行"""
        return self.status == "running"
    
    def get_config_value(self, key: str, default=None):
        """获取配置值"""
        if self.config and key in self.config:
            return self.config[key]
        return default
    
    def get_risk_config_value(self, key: str, default=None):
        """获取风险配置值"""
        if self.risk_config and key in self.risk_config:
            return self.risk_config[key]
        return default
    
    def update_performance(self, **kwargs):
        """更新性能指标"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
