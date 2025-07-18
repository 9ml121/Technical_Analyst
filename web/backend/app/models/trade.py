"""
交易相关模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

# 为了兼容API端点，添加别名
Trade = SimulatedTrade
Position = SimulatedPosition

class SimulatedTrade(Base):
    """模拟交易记录表"""
    __tablename__ = "simulated_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("simulated_accounts.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    signal_id = Column(Integer, ForeignKey("trading_signals.id"), nullable=True)
    
    # 交易基本信息
    symbol = Column(String(10), nullable=False)  # 股票代码
    symbol_name = Column(String(50))  # 股票名称
    side = Column(String(4), nullable=False)  # BUY, SELL
    
    # 价格和数量
    quantity = Column(Integer, nullable=False)  # 交易数量
    price = Column(Float, nullable=False)  # 交易价格
    amount = Column(Float, nullable=False)  # 交易金额
    
    # 费用
    commission = Column(Float, default=0)  # 手续费
    stamp_tax = Column(Float, default=0)  # 印花税
    transfer_fee = Column(Float, default=0)  # 过户费
    total_fee = Column(Float, default=0)  # 总费用
    
    # 交易结果
    realized_pnl = Column(Float, default=0)  # 已实现盈亏
    realized_pnl_rate = Column(Float, default=0)  # 已实现盈亏率
    
    # 交易状态
    status = Column(String(20), default="filled")  # pending, filled, cancelled, failed
    
    # 时间信息
    trade_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 额外信息
    notes = Column(Text)  # 备注
    extra_data = Column(JSON)  # 额外元数据
    
    # 关联关系
    account = relationship("SimulatedAccount", back_populates="trades")
    strategy = relationship("Strategy")
    signal = relationship("TradingSignal", back_populates="trade")
    
    def __repr__(self):
        return f"<SimulatedTrade(symbol='{self.symbol}', side='{self.side}', quantity={self.quantity}, price={self.price})>"
    
    @property
    def is_buy(self):
        """是否为买入"""
        return self.side == "BUY"
    
    @property
    def is_sell(self):
        """是否为卖出"""
        return self.side == "SELL"
    
    def calculate_fees(self):
        """计算交易费用"""
        # 手续费：双向收取，最低5元
        self.commission = max(self.amount * 0.0003, 5.0)
        
        # 印花税：卖出时收取
        if self.is_sell:
            self.stamp_tax = self.amount * 0.001
        
        # 过户费：双向收取
        self.transfer_fee = self.amount * 0.00002
        
        # 总费用
        self.total_fee = self.commission + self.stamp_tax + self.transfer_fee

class TradingSignal(Base):
    """交易信号表"""
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("simulated_accounts.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    
    # 信号基本信息
    symbol = Column(String(10), nullable=False)  # 股票代码
    symbol_name = Column(String(50))  # 股票名称
    signal_type = Column(String(10), nullable=False)  # BUY, SELL
    
    # 信号强度和价格
    signal_strength = Column(Float)  # 信号强度 0.0-1.0
    target_price = Column(Float)  # 目标价格
    current_price = Column(Float)  # 当前价格
    quantity = Column(Integer)  # 建议数量
    
    # 信号状态
    status = Column(String(20), default="pending")  # pending, executed, cancelled, expired
    
    # 执行信息
    executed_price = Column(Float)  # 实际执行价格
    executed_quantity = Column(Integer)  # 实际执行数量
    execution_time = Column(DateTime(timezone=True))  # 执行时间
    
    # 信号生成信息
    generated_time = Column(DateTime(timezone=True), server_default=func.now())
    expire_time = Column(DateTime(timezone=True))  # 过期时间
    
    # 信号原因和元数据
    reason = Column(Text)  # 信号生成原因
    extra_data = Column(JSON)  # 信号元数据（如技术指标值等）
    
    # 关联关系
    account = relationship("SimulatedAccount")
    strategy = relationship("Strategy", back_populates="signals")
    trade = relationship("SimulatedTrade", back_populates="signal", uselist=False)
    
    def __repr__(self):
        return f"<TradingSignal(symbol='{self.symbol}', type='{self.signal_type}', strength={self.signal_strength}, status='{self.status}')>"
    
    @property
    def is_buy_signal(self):
        """是否为买入信号"""
        return self.signal_type == "BUY"
    
    @property
    def is_sell_signal(self):
        """是否为卖出信号"""
        return self.signal_type == "SELL"
    
    @property
    def is_executed(self):
        """是否已执行"""
        return self.status == "executed"
    
    def execute(self, price: float, quantity: int):
        """执行信号"""
        self.status = "executed"
        self.executed_price = price
        self.executed_quantity = quantity
        self.execution_time = func.now()

class SimulatedPosition(Base):
    """模拟持仓表"""
    __tablename__ = "simulated_positions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("simulated_accounts.id"), nullable=False)

    # 持仓基本信息
    symbol = Column(String(10), nullable=False)  # 股票代码
    symbol_name = Column(String(50))  # 股票名称

    # 持仓数量和成本
    quantity = Column(Integer, default=0)  # 持仓数量
    available_quantity = Column(Integer, default=0)  # 可用数量
    avg_cost = Column(Float, default=0)  # 平均成本
    total_cost = Column(Float, default=0)  # 总成本

    # 当前价格和市值
    current_price = Column(Float, default=0)  # 当前价格
    market_value = Column(Float, default=0)  # 市值

    # 盈亏信息
    unrealized_pnl = Column(Float, default=0)  # 浮动盈亏
    unrealized_pnl_rate = Column(Float, default=0)  # 浮动盈亏率
    realized_pnl = Column(Float, default=0)  # 已实现盈亏

    # 时间信息
    first_buy_time = Column(DateTime(timezone=True))  # 首次买入时间
    last_update_time = Column(DateTime(timezone=True), server_default=func.now())  # 最后更新时间

    # 关联关系
    account = relationship("SimulatedAccount", back_populates="positions")

    def __repr__(self):
        return f"<SimulatedPosition(symbol='{self.symbol}', quantity={self.quantity}, avg_cost={self.avg_cost})>"

    def update_market_value(self, current_price: float):
        """更新市值和盈亏"""
        self.current_price = current_price
        self.market_value = self.quantity * current_price
        self.unrealized_pnl = self.market_value - self.total_cost
        if self.total_cost > 0:
            self.unrealized_pnl_rate = (self.unrealized_pnl / self.total_cost) * 100
        self.last_update_time = func.now()

    def add_position(self, quantity: int, price: float):
        """增加持仓"""
        if self.quantity == 0:
            # 首次买入
            self.quantity = quantity
            self.available_quantity = quantity
            self.avg_cost = price
            self.total_cost = quantity * price
            self.first_buy_time = func.now()
        else:
            # 加仓
            new_total_cost = self.total_cost + (quantity * price)
            new_quantity = self.quantity + quantity
            self.avg_cost = new_total_cost / new_quantity
            self.quantity = new_quantity
            self.available_quantity += quantity
            self.total_cost = new_total_cost

        self.last_update_time = func.now()

    def reduce_position(self, quantity: int, price: float):
        """减少持仓"""
        if quantity > self.available_quantity:
            raise ValueError("减仓数量超过可用数量")

        # 计算已实现盈亏
        cost_per_share = self.total_cost / self.quantity
        realized_pnl = (price - cost_per_share) * quantity
        self.realized_pnl += realized_pnl

        # 更新持仓
        self.quantity -= quantity
        self.available_quantity -= quantity
        self.total_cost -= cost_per_share * quantity

        if self.quantity == 0:
            # 清仓
            self.avg_cost = 0
            self.total_cost = 0

        self.last_update_time = func.now()
        return realized_pnl

# 为了兼容API端点，添加别名
Trade = SimulatedTrade
Position = SimulatedPosition
