"""
性能分析模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class AccountPerformance(Base):
    """账户表现记录表"""
    __tablename__ = "account_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("simulated_accounts.id"), nullable=False)
    
    # 时间维度
    date = Column(Date, nullable=False, index=True)
    time_frame = Column(String(10), nullable=False, index=True)  # day, week, month, year
    period_label = Column(String(50), nullable=False)  # 如"2024-01-16", "2024年第3周"等
    
    # 资产信息
    start_asset = Column(Float, nullable=False)  # 期初资产
    end_asset = Column(Float, nullable=False)  # 期末资产
    
    # 收益信息
    return_amount = Column(Float, nullable=False)  # 收益金额
    return_rate = Column(Float, nullable=False)  # 收益率
    cumulative_return_rate = Column(Float, nullable=False)  # 累计收益率
    
    # 风险指标
    max_drawdown = Column(Float, default=0)  # 最大回撤
    volatility = Column(Float, default=0)  # 波动率
    sharpe_ratio = Column(Float, default=0)  # 夏普比率
    
    # 交易统计
    trade_count = Column(Integer, default=0)  # 交易次数
    win_count = Column(Integer, default=0)  # 盈利次数
    win_rate = Column(Float, default=0)  # 胜率
    
    # 持仓信息
    position_count = Column(Integer, default=0)  # 持仓数量
    position_ratio = Column(Float, default=0)  # 仓位比例
    
    # 基准对比
    benchmark_return = Column(Float, default=0)  # 基准收益率
    excess_return = Column(Float, default=0)  # 超额收益
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    account = relationship("SimulatedAccount", back_populates="performance_records")
    
    def __repr__(self):
        return f"<AccountPerformance(account_id={self.account_id}, date={self.date}, return_rate={self.return_rate}%)>"
    
    @property
    def is_profitable(self):
        """是否盈利"""
        return self.return_amount > 0

class StrategyPerformance(Base):
    """策略表现记录表"""
    __tablename__ = "strategy_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    
    # 时间信息
    date = Column(Date, nullable=False, index=True)
    time_frame = Column(String(10), nullable=False)  # day, week, month, year
    
    # 收益指标
    total_return = Column(Float, default=0)  # 总收益率
    daily_return = Column(Float, default=0)  # 日收益率
    cumulative_return = Column(Float, default=0)  # 累计收益率
    
    # 风险指标
    max_drawdown = Column(Float, default=0)  # 最大回撤
    volatility = Column(Float, default=0)  # 波动率
    sharpe_ratio = Column(Float, default=0)  # 夏普比率
    sortino_ratio = Column(Float, default=0)  # 索提诺比率
    calmar_ratio = Column(Float, default=0)  # 卡尔马比率
    
    # 交易统计
    trade_count = Column(Integer, default=0)  # 交易次数
    win_count = Column(Integer, default=0)  # 盈利次数
    win_rate = Column(Float, default=0)  # 胜率
    avg_win = Column(Float, default=0)  # 平均盈利
    avg_loss = Column(Float, default=0)  # 平均亏损
    profit_factor = Column(Float, default=0)  # 盈利因子
    
    # 持仓统计
    avg_holding_period = Column(Float, default=0)  # 平均持仓期
    max_positions = Column(Integer, default=0)  # 最大持仓数
    turnover_rate = Column(Float, default=0)  # 换手率
    
    # 基准对比
    benchmark_return = Column(Float, default=0)  # 基准收益率
    alpha = Column(Float, default=0)  # 阿尔法
    beta = Column(Float, default=0)  # 贝塔
    information_ratio = Column(Float, default=0)  # 信息比率
    
    # 详细数据
    metadata = Column(JSON)  # 额外的性能数据
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    strategy = relationship("Strategy", back_populates="performance_records")
    
    def __repr__(self):
        return f"<StrategyPerformance(strategy_id={self.strategy_id}, date={self.date}, return={self.total_return}%)>"
    
    def calculate_ratios(self, risk_free_rate: float = 0.03):
        """计算各种比率"""
        # 夏普比率
        if self.volatility > 0:
            self.sharpe_ratio = (self.total_return - risk_free_rate) / self.volatility
        
        # 卡尔马比率
        if self.max_drawdown > 0:
            self.calmar_ratio = self.total_return / abs(self.max_drawdown)
        
        # 盈利因子
        if self.avg_loss != 0:
            self.profit_factor = abs(self.avg_win / self.avg_loss)

class BenchmarkPerformance(Base):
    """基准表现记录表"""
    __tablename__ = "benchmark_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    benchmark_code = Column(String(10), nullable=False, index=True)  # 基准代码
    benchmark_name = Column(String(50), nullable=False)  # 基准名称
    
    # 时间信息
    date = Column(Date, nullable=False, index=True)
    time_frame = Column(String(10), nullable=False)  # day, week, month, year
    
    # 收益指标
    return_rate = Column(Float, nullable=False)  # 收益率
    cumulative_return_rate = Column(Float, nullable=False)  # 累计收益率
    
    # 风险指标
    max_drawdown = Column(Float, default=0)  # 最大回撤
    volatility = Column(Float, default=0)  # 波动率
    sharpe_ratio = Column(Float, default=0)  # 夏普比率
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<BenchmarkPerformance(code='{self.benchmark_code}', date={self.date}, return={self.return_rate}%)>"
