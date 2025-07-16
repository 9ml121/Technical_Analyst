"""
模拟账户模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class SimulatedAccount(Base):
    """模拟账户表"""
    __tablename__ = "simulated_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 暂时允许为空
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 资金信息
    initial_capital = Column(Float, nullable=False)  # 初始资金
    current_capital = Column(Float, nullable=False)  # 当前资金
    available_capital = Column(Float, nullable=False, default=0)  # 可用资金
    frozen_capital = Column(Float, default=0)  # 冻结资金
    
    # 持仓信息
    total_market_value = Column(Float, default=0)  # 持仓市值
    total_asset = Column(Float, default=0)  # 总资产
    
    # 收益信息
    total_profit = Column(Float, default=0)  # 累计盈亏
    total_return_rate = Column(Float, default=0)  # 累计收益率
    today_profit = Column(Float, default=0)  # 今日盈亏
    today_return_rate = Column(Float, default=0)  # 今日收益率
    
    # 风险指标
    max_drawdown = Column(Float, default=0)  # 最大回撤
    win_rate = Column(Float, default=0)  # 胜率
    sharpe_ratio = Column(Float, default=0)  # 夏普比率
    
    # 交易统计
    total_trades = Column(Integer, default=0)  # 总交易次数
    win_trades = Column(Integer, default=0)  # 盈利交易次数
    
    # 策略关联
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    
    # 状态和配置
    status = Column(String(20), default="active")  # active, suspended, closed
    config = Column(JSON)  # 账户配置
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="accounts")
    strategy = relationship("Strategy", back_populates="accounts")
    trades = relationship("SimulatedTrade", back_populates="account")
    positions = relationship("SimulatedPosition", back_populates="account")
    performance_records = relationship("AccountPerformance", back_populates="account")
    
    def __repr__(self):
        return f"<SimulatedAccount(id={self.id}, name='{self.name}', capital={self.current_capital})>"
    
    @property
    def position_ratio(self):
        """仓位比例"""
        if self.total_asset > 0:
            return self.total_market_value / self.total_asset
        return 0
    
    def update_asset(self):
        """更新总资产"""
        self.total_asset = self.current_capital + self.total_market_value
        self.available_capital = self.current_capital - self.frozen_capital

class SimulatedPosition(Base):
    """模拟持仓表"""
    __tablename__ = "simulated_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("simulated_accounts.id"), nullable=False)
    symbol = Column(String(10), nullable=False)  # 股票代码
    symbol_name = Column(String(50))  # 股票名称
    
    # 持仓信息
    quantity = Column(Integer, nullable=False)  # 持仓数量
    avg_cost = Column(Float, nullable=False)  # 平均成本
    current_price = Column(Float, default=0)  # 当前价格
    
    # 盈亏信息
    market_value = Column(Float, default=0)  # 市值
    unrealized_pnl = Column(Float, default=0)  # 浮动盈亏
    unrealized_pnl_rate = Column(Float, default=0)  # 浮动盈亏率
    
    # 交易信息
    first_buy_date = Column(DateTime(timezone=True))  # 首次买入日期
    last_trade_date = Column(DateTime(timezone=True))  # 最后交易日期
    holding_days = Column(Integer, default=0)  # 持有天数
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    account = relationship("SimulatedAccount", back_populates="positions")
    
    def __repr__(self):
        return f"<SimulatedPosition(symbol='{self.symbol}', quantity={self.quantity}, cost={self.avg_cost})>"
    
    def update_market_value(self, current_price: float):
        """更新市值和盈亏"""
        self.current_price = current_price
        self.market_value = self.quantity * current_price
        cost_value = self.quantity * self.avg_cost
        self.unrealized_pnl = self.market_value - cost_value
        if cost_value > 0:
            self.unrealized_pnl_rate = (self.unrealized_pnl / cost_value) * 100
