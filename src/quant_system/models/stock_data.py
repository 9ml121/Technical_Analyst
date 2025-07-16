"""
股票数据模型

定义股票相关的数据结构和模型
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

@dataclass
class StockData:
    """股票基础数据模型"""
    code: str                    # 股票代码
    name: str                    # 股票名称
    date: date                   # 交易日期
    open_price: float           # 开盘价
    close_price: float          # 收盘价
    high_price: float           # 最高价
    low_price: float            # 最低价
    volume: int                 # 成交量
    amount: float               # 成交额
    pre_close: Optional[float] = None    # 昨收价
    change: Optional[float] = None       # 涨跌额
    pct_change: Optional[float] = None   # 涨跌幅
    turnover_rate: Optional[float] = None # 换手率
    
    def __post_init__(self):
        """数据验证和计算"""
        if self.pre_close and not self.change:
            self.change = self.close_price - self.pre_close
        
        if self.pre_close and not self.pct_change:
            self.pct_change = self.change / self.pre_close if self.pre_close != 0 else 0

@dataclass
class StockInfo:
    """股票基本信息模型"""
    code: str                    # 股票代码
    name: str                    # 股票名称
    market: str                  # 市场 (SH/SZ/HK)
    industry: Optional[str] = None       # 行业
    sector: Optional[str] = None         # 板块
    list_date: Optional[date] = None     # 上市日期
    market_cap: Optional[float] = None   # 总市值
    float_cap: Optional[float] = None    # 流通市值
    pe_ratio: Optional[float] = None     # 市盈率
    pb_ratio: Optional[float] = None     # 市净率
    roe: Optional[float] = None          # ROE
    debt_ratio: Optional[float] = None   # 负债率

@dataclass
class MarketIndex:
    """市场指数数据模型"""
    code: str                    # 指数代码
    name: str                    # 指数名称
    date: date                   # 交易日期
    open_price: float           # 开盘点位
    close_price: float          # 收盘点位
    high_price: float           # 最高点位
    low_price: float            # 最低点位
    volume: int                 # 成交量
    amount: float               # 成交额
    change: Optional[float] = None       # 涨跌点数
    pct_change: Optional[float] = None   # 涨跌幅

@dataclass
class TradingSession:
    """交易时段信息"""
    market: str                  # 市场
    session_name: str           # 时段名称
    start_time: str             # 开始时间
    end_time: str               # 结束时间
    is_trading: bool            # 是否交易时间
    
class StockDataValidator:
    """股票数据验证器"""
    
    @staticmethod
    def validate_stock_code(code: str, market: str = "A") -> bool:
        """验证股票代码格式"""
        if not code or not isinstance(code, str):
            return False
        
        if market == "A":  # A股
            return (
                (code.startswith("00") and len(code) == 6) or  # 深市
                (code.startswith("30") and len(code) == 6) or  # 创业板
                (code.startswith("60") and len(code) == 6) or  # 沪市
                (code.startswith("68") and len(code) == 6)     # 科创板
            )
        elif market == "HK":  # 港股
            return len(code) == 5 and code.isdigit()
        
        return False
    
    @staticmethod
    def validate_price_data(data) -> bool:
        """验证价格数据的合理性"""
        # 如果传入的是单个价格值
        if isinstance(data, (int, float)):
            return 0 < data <= 10000  # 价格合理范围
        
        # 如果传入的是StockData对象
        if hasattr(data, 'open_price'):
            errors = []
            
            # 价格必须为正数
            if data.open_price <= 0:
                errors.append("开盘价必须大于0")
            if data.close_price <= 0:
                errors.append("收盘价必须大于0")
            if data.high_price <= 0:
                errors.append("最高价必须大于0")
            if data.low_price <= 0:
                errors.append("最低价必须大于0")
        
            # 价格关系验证
            if data.high_price < max(data.open_price, data.close_price, data.low_price):
                errors.append("最高价不能小于开盘价、收盘价或最低价")
            
            if data.low_price > min(data.open_price, data.close_price, data.high_price):
                errors.append("最低价不能大于开盘价、收盘价或最高价")
            
            # 成交量和成交额验证
            if hasattr(data, 'volume') and data.volume < 0:
                errors.append("成交量不能为负数")
            if hasattr(data, 'amount') and data.amount < 0:
                errors.append("成交额不能为负数")
            
            # 涨跌幅合理性验证 (A股涨跌停限制)
            if hasattr(data, 'pct_change') and data.pct_change and abs(data.pct_change) > 0.20:  # 20%涨跌停
                errors.append("涨跌幅超过合理范围")
            
            return len(errors) == 0
        
        return False
    
    @staticmethod
    def validate_volume_data(data) -> bool:
        """验证成交量数据的合理性"""
        # 如果传入的是单个成交量值
        if isinstance(data, (int, float)):
            return data >= 0
        
        # 如果传入的是StockData对象
        if hasattr(data, 'volume'):
            return data.volume >= 0
        
        return False

class StockDataProcessor:
    """股票数据处理器"""
    
    @staticmethod
    def calculate_technical_indicators(data_list: List[StockData]) -> Dict[str, Any]:
        """计算技术指标"""
        if not data_list:
            return {}
        
        # 按日期排序
        sorted_data = sorted(data_list, key=lambda x: x.date)
        prices = [d.close_price for d in sorted_data]
        volumes = [d.volume for d in sorted_data]
        
        indicators = {}
        
        # 移动平均线
        if len(prices) >= 5:
            indicators['ma5'] = sum(prices[-5:]) / 5
        if len(prices) >= 10:
            indicators['ma10'] = sum(prices[-10:]) / 10
        if len(prices) >= 20:
            indicators['ma20'] = sum(prices[-20:]) / 20
        
        # 成交量移动平均
        if len(volumes) >= 5:
            indicators['vol_ma5'] = sum(volumes[-5:]) / 5
        
        # 价格波动率 (最近20天)
        if len(prices) >= 20:
            recent_prices = prices[-20:]
            returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                      for i in range(1, len(recent_prices))]
            volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5
            indicators['volatility_20d'] = volatility
        
        return indicators
    
    @staticmethod
    def detect_price_patterns(data_list: List[StockData]) -> List[str]:
        """检测价格模式"""
        if len(data_list) < 3:
            return []
        
        patterns = []
        sorted_data = sorted(data_list, key=lambda x: x.date)
        recent_data = sorted_data[-3:]  # 最近3天
        
        # 连续上涨
        if all(recent_data[i].close_price > recent_data[i-1].close_price 
               for i in range(1, len(recent_data))):
            patterns.append("连续上涨")
        
        # 连续下跌
        if all(recent_data[i].close_price < recent_data[i-1].close_price 
               for i in range(1, len(recent_data))):
            patterns.append("连续下跌")
        
        # 放量上涨
        if (len(recent_data) >= 2 and 
            recent_data[-1].close_price > recent_data[-2].close_price and
            recent_data[-1].volume > recent_data[-2].volume * 1.5):
            patterns.append("放量上涨")
        
        return patterns
