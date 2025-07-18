"""
基础数据模型 - 微服务架构共享模型
定义量化交易系统的核心数据结构和模型
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional, Any
from enum import Enum

# 枚举类型定义


class SignalType(Enum):
    """信号类型枚举"""
    BUY = "buy"                    # 买入信号
    SELL = "sell"                  # 卖出信号
    HOLD = "hold"                  # 持有信号


class TradeAction(Enum):
    """交易动作枚举"""
    BUY = "buy"                    # 买入
    SELL = "sell"                  # 卖出


class OrderType(Enum):
    """订单类型枚举"""
    MARKET = "market"              # 市价单
    LIMIT = "limit"                # 限价单
    STOP = "stop"                  # 止损单
    STOP_LIMIT = "stop_limit"      # 止损限价单


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"            # 待成交
    FILLED = "filled"              # 已成交
    CANCELLED = "cancelled"        # 已取消
    REJECTED = "rejected"          # 已拒绝


class StrategyType(Enum):
    """策略类型枚举"""
    MOMENTUM = "momentum"           # 动量策略
    MEAN_REVERSION = "mean_reversion"  # 均值回归策略
    BREAKOUT = "breakout"          # 突破策略
    CUSTOM = "custom"              # 自定义策略

# 核心数据模型


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
        self.unrealized_pnl = self.market_value - \
            (self.quantity * self.avg_cost)
        if self.quantity * self.avg_cost > 0:
            self.unrealized_pnl_pct = self.unrealized_pnl / \
                (self.quantity * self.avg_cost)
        else:
            self.unrealized_pnl_pct = 0.0


@dataclass
class TradeRecord:
    """交易记录模型"""
    trade_id: str                  # 交易ID
    stock_code: str                # 股票代码
    stock_name: str                # 股票名称
    action: TradeAction            # 交易动作
    quantity: int                  # 交易数量
    price: float                   # 交易价格
    amount: float                  # 交易金额
    commission: float              # 手续费
    date: date                     # 交易日期
    time: datetime                 # 交易时间
    stamp_tax: float = 0.0         # 印花税
    profit_loss: Optional[float] = None     # 盈亏金额
    profit_loss_pct: Optional[float] = None  # 盈亏比例
    holding_days: Optional[int] = None      # 持仓天数
    reason: str = ""               # 交易原因
    strategy_name: str = ""        # 策略名称


@dataclass
class Order:
    """订单模型"""
    order_id: str                  # 订单ID
    stock_code: str                # 股票代码
    action: TradeAction            # 交易动作
    order_type: OrderType          # 订单类型
    quantity: int                  # 数量
    price: float                   # 价格
    order_time: datetime           # 下单时间
    status: OrderStatus = OrderStatus.PENDING  # 订单状态
    filled_quantity: int = 0       # 已成交数量
    filled_price: float = 0.0      # 成交价格
    fill_time: Optional[datetime] = None  # 成交时间
    commission: float = 0.0        # 手续费
    reason: str = ""               # 下单原因


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
        self.market_value = sum(
            pos.market_value for pos in self.positions.values())
        self.total_value = self.cash + self.market_value


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
class BacktestConfig:
    """回测配置模型"""
    start_date: date               # 回测开始日期
    end_date: date                 # 回测结束日期
    initial_capital: float         # 初始资金
    max_positions: int = 5         # 最大持仓数量
    position_size_pct: float = 0.20  # 单只股票仓位比例
    commission_rate: float = 0.0003  # 手续费率
    stamp_tax_rate: float = 0.001    # 印花税率(卖出时)
    slippage_rate: float = 0.001     # 滑点率
    stop_loss_pct: float = 0.05      # 止损比例
    benchmark: str = "000300.SH"     # 基准指数

    def __post_init__(self):
        """验证配置参数"""
        if self.start_date >= self.end_date:
            raise ValueError("开始日期必须早于结束日期")
        if self.initial_capital <= 0:
            raise ValueError("初始资金必须大于0")
        if not (0 < self.position_size_pct <= 1):
            raise ValueError("仓位比例必须在0-1之间")


@dataclass
class DailyPerformance:
    """日度绩效模型"""
    date: date                     # 日期
    portfolio_value: float         # 组合价值
    cash: float                    # 现金
    market_value: float            # 持仓市值
    daily_return: float            # 日收益率
    cumulative_return: float       # 累计收益率
    drawdown: float                # 回撤
    benchmark_return: float = 0.0  # 基准日收益率
    positions_count: int = 0       # 持仓数量
    turnover: float = 0.0          # 换手率


@dataclass
class BacktestResult:
    """回测结果模型"""
    config: BacktestConfig         # 回测配置
    start_date: date              # 实际开始日期
    end_date: date                # 实际结束日期
    initial_capital: float        # 初始资金
    final_capital: float          # 最终资金
    total_return: float           # 总收益率
    annual_return: float          # 年化收益率
    max_drawdown: float           # 最大回撤
    sharpe_ratio: float           # 夏普比率
    sortino_ratio: float          # 索提诺比率
    calmar_ratio: float           # 卡玛比率
    win_rate: float               # 胜率
    profit_loss_ratio: float      # 盈亏比
    total_trades: int             # 总交易次数
    avg_holding_days: float       # 平均持仓天数
    turnover_rate: float          # 换手率
    benchmark_return: float       # 基准收益率
    excess_return: float          # 超额收益
    tracking_error: float         # 跟踪误差
    information_ratio: float      # 信息比率
    volatility: float             # 波动率
    downside_volatility: float    # 下行波动率

    # 详细记录
    trade_records: List[TradeRecord] = field(default_factory=list)
    daily_performance: List[DailyPerformance] = field(default_factory=list)
    monthly_returns: Dict[str, float] = field(default_factory=dict)
    yearly_returns: Dict[str, float] = field(default_factory=dict)


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


@dataclass
class RiskMetrics:
    """风险指标模型"""
    var_95: float                  # 95% VaR
    var_99: float                  # 99% VaR
    cvar_95: float                 # 95% CVaR
    cvar_99: float                 # 99% CVaR
    max_consecutive_losses: int    # 最大连续亏损次数
    max_consecutive_loss_days: int  # 最大连续亏损天数
    max_single_loss: float         # 最大单次亏损
    max_single_loss_pct: float     # 最大单次亏损比例
