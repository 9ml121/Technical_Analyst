"""
策略相关数据模型

定义选股策略、交易策略等相关的数据结构
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Optional, Any
from enum import Enum

class StrategyType(Enum):
    """策略类型枚举"""
    MOMENTUM = "momentum"           # 动量策略
    MEAN_REVERSION = "mean_reversion"  # 均值回归策略
    BREAKOUT = "breakout"          # 突破策略
    CUSTOM = "custom"              # 自定义策略

class SignalType(Enum):
    """信号类型枚举"""
    BUY = "buy"                    # 买入信号
    SELL = "sell"                  # 卖出信号
    HOLD = "hold"                  # 持有信号

@dataclass
class SelectionCriteria:
    """选股条件模型"""
    consecutive_days: int = 3                    # 连续交易日数
    min_total_return: float = 0.15              # 最小总收益率
    max_drawdown: float = 0.05                  # 最大回撤
    exclude_limit_up_first_day: bool = True     # 排除首日涨停
    
    # 价格筛选
    min_stock_price: Optional[float] = None     # 最小股价
    max_stock_price: Optional[float] = None     # 最大股价
    min_market_cap: Optional[float] = None      # 最小市值
    max_market_cap: Optional[float] = None      # 最大市值
    
    # 成交量筛选
    min_avg_volume: Optional[float] = None      # 最小平均成交额
    min_turnover_rate: Optional[float] = None   # 最小换手率
    max_turnover_rate: Optional[float] = None   # 最大换手率
    
    # 技术指标
    enable_technical: bool = False              # 启用技术指标
    rsi_min: Optional[float] = None            # RSI下限
    rsi_max: Optional[float] = None            # RSI上限
    require_macd_golden_cross: bool = False     # 要求MACD金叉
    require_ma_bullish: bool = False            # 要求均线多头
    
    # 基本面筛选
    enable_fundamental: bool = False            # 启用基本面筛选
    min_roe: Optional[float] = None            # 最小ROE
    max_pe_ratio: Optional[float] = None       # 最大PE
    min_revenue_growth: Optional[float] = None  # 最小营收增长率
    max_debt_ratio: Optional[float] = None     # 最大负债率
    
    # 行业筛选
    excluded_industries: List[str] = field(default_factory=list)  # 排除行业
    included_sectors: List[str] = field(default_factory=list)     # 包含板块
    exclude_new_stocks: bool = True             # 排除新股
    new_stock_days_limit: int = 60             # 新股天数限制

@dataclass
class TradingRule:
    """交易规则模型"""
    name: str                      # 规则名称
    description: str               # 规则描述
    condition: str                 # 条件表达式
    action: SignalType            # 执行动作
    priority: int = 1             # 优先级
    enabled: bool = True          # 是否启用

@dataclass
class TradingStrategy:
    """交易策略模型"""
    name: str                      # 策略名称
    strategy_type: StrategyType    # 策略类型
    description: str               # 策略描述
    buy_rules: List[TradingRule] = field(default_factory=list)   # 买入规则
    sell_rules: List[TradingRule] = field(default_factory=list)  # 卖出规则
    risk_rules: List[TradingRule] = field(default_factory=list)  # 风控规则
    parameters: Dict[str, Any] = field(default_factory=dict)     # 策略参数
    
    def add_buy_rule(self, rule: TradingRule):
        """添加买入规则"""
        self.buy_rules.append(rule)
    
    def add_sell_rule(self, rule: TradingRule):
        """添加卖出规则"""
        self.sell_rules.append(rule)
    
    def add_risk_rule(self, rule: TradingRule):
        """添加风控规则"""
        self.risk_rules.append(rule)

@dataclass
class TradingSignal:
    """交易信号模型"""
    stock_code: str               # 股票代码
    signal_type: SignalType       # 信号类型
    signal_time: date            # 信号时间
    price: float                 # 信号价格
    confidence: float            # 信号置信度 (0-1)
    reason: str                  # 信号原因
    strategy_name: str           # 策略名称
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外信息

@dataclass
class Position:
    """持仓模型"""
    stock_code: str              # 股票代码
    stock_name: str              # 股票名称
    quantity: int                # 持仓数量
    avg_cost: float              # 平均成本
    current_price: float         # 当前价格
    market_value: float          # 市值
    unrealized_pnl: float        # 浮动盈亏
    unrealized_pnl_pct: float    # 浮动盈亏比例
    buy_date: date               # 买入日期
    holding_days: int            # 持仓天数
    
    def update_price(self, new_price: float):
        """更新当前价格"""
        self.current_price = new_price
        self.market_value = self.quantity * new_price
        self.unrealized_pnl = self.market_value - (self.quantity * self.avg_cost)
        self.unrealized_pnl_pct = self.unrealized_pnl / (self.quantity * self.avg_cost)

@dataclass
class Portfolio:
    """投资组合模型"""
    total_value: float           # 总资产
    cash: float                  # 现金
    market_value: float          # 持仓市值
    positions: Dict[str, Position] = field(default_factory=dict)  # 持仓明细
    daily_returns: List[float] = field(default_factory=list)     # 日收益率
    
    def add_position(self, position: Position):
        """添加持仓"""
        self.positions[position.stock_code] = position
        self._update_portfolio_value()
    
    def remove_position(self, stock_code: str):
        """移除持仓"""
        if stock_code in self.positions:
            del self.positions[stock_code]
            self._update_portfolio_value()
    
    def _update_portfolio_value(self):
        """更新组合价值"""
        self.market_value = sum(pos.market_value for pos in self.positions.values())
        self.total_value = self.cash + self.market_value

@dataclass
class StrategyPerformance:
    """策略绩效模型"""
    strategy_name: str           # 策略名称
    start_date: date            # 开始日期
    end_date: date              # 结束日期
    total_return: float         # 总收益率
    annual_return: float        # 年化收益率
    max_drawdown: float         # 最大回撤
    sharpe_ratio: float         # 夏普比率
    win_rate: float             # 胜率
    profit_loss_ratio: float    # 盈亏比
    total_trades: int           # 总交易次数
    avg_holding_days: float     # 平均持仓天数
    benchmark_return: float     # 基准收益率
    excess_return: float        # 超额收益
    volatility: float           # 波动率
    
    def calculate_metrics(self, returns: List[float], benchmark_returns: List[float] = None):
        """计算绩效指标"""
        if not returns:
            return
        
        import numpy as np
        
        # 总收益率
        self.total_return = (1 + np.array(returns)).prod() - 1
        
        # 年化收益率
        trading_days = len(returns)
        self.annual_return = (1 + self.total_return) ** (252 / trading_days) - 1
        
        # 波动率
        self.volatility = np.std(returns) * np.sqrt(252)
        
        # 夏普比率 (假设无风险利率为3%)
        risk_free_rate = 0.03
        self.sharpe_ratio = (self.annual_return - risk_free_rate) / self.volatility if self.volatility > 0 else 0
        
        # 最大回撤
        cumulative_returns = (1 + np.array(returns)).cumprod()
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        self.max_drawdown = abs(drawdowns.min())
        
        # 基准对比
        if benchmark_returns:
            self.benchmark_return = (1 + np.array(benchmark_returns)).prod() - 1
            self.excess_return = self.total_return - self.benchmark_return
