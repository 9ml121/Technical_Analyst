"""
市场数据模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, JSON
from sqlalchemy.sql import func

from app.core.database import Base

class MarketIndex(Base):
    """市场指数表"""
    __tablename__ = "market_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), nullable=False, index=True)  # 指数代码
    name = Column(String(50), nullable=False)  # 指数名称
    
    # 价格信息
    current_value = Column(Float, nullable=False)  # 当前点位
    change_value = Column(Float, default=0)  # 涨跌点数
    change_percent = Column(Float, default=0)  # 涨跌幅度
    
    # 交易信息
    volume = Column(Integer, default=0)  # 成交量
    amount = Column(Float, default=0)  # 成交额
    
    # 其他信息
    open_value = Column(Float)  # 开盘价
    high_value = Column(Float)  # 最高价
    low_value = Column(Float)  # 最低价
    prev_close = Column(Float)  # 昨收价
    
    # 时间信息
    trade_date = Column(Date, nullable=False)  # 交易日期
    timestamp = Column(DateTime(timezone=True), server_default=func.now())  # 更新时间
    
    def __repr__(self):
        return f"<MarketIndex(code='{self.code}', name='{self.name}', value={self.current_value})>"
    
    @property
    def is_rising(self):
        """是否上涨"""
        return self.change_value > 0
    
    @property
    def is_falling(self):
        """是否下跌"""
        return self.change_value < 0

class MarketStats(Base):
    """市场统计数据表"""
    __tablename__ = "market_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(Date, nullable=False, index=True)  # 交易日期
    
    # 涨跌统计
    rise_count = Column(Integer, default=0)  # 上涨股票数
    fall_count = Column(Integer, default=0)  # 下跌股票数
    flat_count = Column(Integer, default=0)  # 平盘股票数
    
    # 极端情况
    limit_up_count = Column(Integer, default=0)  # 涨停股票数
    limit_down_count = Column(Integer, default=0)  # 跌停股票数
    
    # 交易统计
    total_volume = Column(Integer, default=0)  # 总成交量
    total_amount = Column(Float, default=0)  # 总成交额
    active_stocks = Column(Integer, default=0)  # 活跃股票数
    suspended_stocks = Column(Integer, default=0)  # 停牌股票数
    
    # 市场情绪指标
    advance_decline_ratio = Column(Float, default=0)  # 涨跌比
    market_sentiment = Column(String(20))  # 市场情绪：bullish, bearish, neutral
    
    # 更新时间
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MarketStats(date={self.trade_date}, rise={self.rise_count}, fall={self.fall_count})>"
    
    @property
    def total_stocks(self):
        """总股票数"""
        return self.rise_count + self.fall_count + self.flat_count
    
    @property
    def rise_ratio(self):
        """上涨比例"""
        total = self.total_stocks
        return (self.rise_count / total * 100) if total > 0 else 0
    
    def calculate_sentiment(self):
        """计算市场情绪"""
        if self.advance_decline_ratio > 1.5:
            self.market_sentiment = "bullish"
        elif self.advance_decline_ratio < 0.7:
            self.market_sentiment = "bearish"
        else:
            self.market_sentiment = "neutral"

class StockQuote(Base):
    """股票行情表"""
    __tablename__ = "stock_quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)  # 股票代码
    symbol_name = Column(String(50))  # 股票名称
    
    # 价格信息
    current_price = Column(Float, nullable=False)  # 当前价格
    change_value = Column(Float, default=0)  # 涨跌额
    change_percent = Column(Float, default=0)  # 涨跌幅
    
    # OHLC数据
    open_price = Column(Float)  # 开盘价
    high_price = Column(Float)  # 最高价
    low_price = Column(Float)  # 最低价
    prev_close = Column(Float)  # 昨收价
    
    # 交易数据
    volume = Column(Integer, default=0)  # 成交量
    amount = Column(Float, default=0)  # 成交额
    turnover_rate = Column(Float, default=0)  # 换手率
    
    # 买卖盘
    bid_price = Column(Float)  # 买一价
    ask_price = Column(Float)  # 卖一价
    bid_volume = Column(Integer)  # 买一量
    ask_volume = Column(Integer)  # 卖一量
    
    # 技术指标（可选）
    ma5 = Column(Float)  # 5日均线
    ma10 = Column(Float)  # 10日均线
    ma20 = Column(Float)  # 20日均线
    rsi = Column(Float)  # RSI指标
    
    # 时间信息
    trade_date = Column(Date, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # 额外信息
    metadata = Column(JSON)  # 额外的行情数据
    
    def __repr__(self):
        return f"<StockQuote(symbol='{self.symbol}', price={self.current_price}, change={self.change_percent}%)>"
    
    @property
    def is_limit_up(self):
        """是否涨停"""
        return abs(self.change_percent - 10.0) < 0.01
    
    @property
    def is_limit_down(self):
        """是否跌停"""
        return abs(self.change_percent + 10.0) < 0.01
    
    @property
    def is_rising(self):
        """是否上涨"""
        return self.change_value > 0
